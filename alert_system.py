#!/usr/bin/env python3
"""
IoT Alert System - Monitors sensor data and generates alerts for critical conditions
Monitors InfluxDB for:
  - Low soil moisture (< 30%)
  - Critical low moisture (< 20%)
  - Low battery voltage (< 3.3V)
  - High temperature (> 35°C)
  - Sensor offline (no data for 5+ minutes)
"""

import os
import sys
import time
import logging
import argparse
from datetime import datetime, timezone
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AlertSystem:
    """Monitor sensor data and generate alerts for critical conditions"""
    
    # Alert thresholds
    MOISTURE_LOW = 30.0
    MOISTURE_CRITICAL = 20.0
    BATTERY_LOW = 3.3
    TEMP_HIGH = 35.0
    SENSOR_TIMEOUT_SECONDS = 300  # 5 minutes
    
    def __init__(self, influxdb_url, token, org, bucket, alert_bucket="alerts"):
        """Initialize alert system"""
        self.client = InfluxDBClient(url=influxdb_url, token=token, org=org)
        self.query_api = self.client.query_api()
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.org = org
        self.bucket = bucket
        self.alert_bucket = alert_bucket
        
        # Track alert state to prevent spam
        self.alert_state = {}
        
        logger.info(f"Alert system initialized - monitoring bucket: {bucket}")
    
    def check_soil_moisture(self):
        """Check for low soil moisture conditions"""
        query = f'''
        from(bucket: "{self.bucket}")
          |> range(start: -5m)
          |> filter(fn: (r) => r._measurement == "mqtt_consumer")
          |> filter(fn: (r) => r._field == "soil_moisture_percent")
          |> last()
        '''
        
        try:
            result = self.query_api.query(query)
            for table in result:
                for record in table.records:
                    moisture = record.get_value()
                    device_id = record.values.get('device_id', 'unknown')
                    
                    if moisture < self.MOISTURE_CRITICAL:
                        self._trigger_alert(
                            device_id=device_id,
                            alert_type="CRITICAL_LOW_MOISTURE",
                            severity="critical",
                            message=f"Critical: Soil moisture at {moisture:.1f}% (threshold: {self.MOISTURE_CRITICAL}%)",
                            value=moisture
                        )
                    elif moisture < self.MOISTURE_LOW:
                        self._trigger_alert(
                            device_id=device_id,
                            alert_type="LOW_MOISTURE",
                            severity="warning",
                            message=f"Warning: Soil moisture at {moisture:.1f}% (threshold: {self.MOISTURE_LOW}%)",
                            value=moisture
                        )
                    else:
                        # Clear alert if moisture is back to normal
                        self._clear_alert(device_id, "LOW_MOISTURE")
                        self._clear_alert(device_id, "CRITICAL_LOW_MOISTURE")
                        
        except Exception as e:
            logger.error(f"Error checking soil moisture: {e}")
    
    def check_battery_voltage(self):
        """Check for low battery conditions"""
        query = f'''
        from(bucket: "{self.bucket}")
          |> range(start: -5m)
          |> filter(fn: (r) => r._measurement == "mqtt_consumer")
          |> filter(fn: (r) => r._field == "battery_voltage")
          |> last()
        '''
        
        try:
            result = self.query_api.query(query)
            for table in result:
                for record in table.records:
                    voltage = record.get_value()
                    device_id = record.values.get('device_id', 'unknown')
                    
                    if voltage < self.BATTERY_LOW:
                        self._trigger_alert(
                            device_id=device_id,
                            alert_type="LOW_BATTERY",
                            severity="warning",
                            message=f"Warning: Battery voltage at {voltage:.2f}V (threshold: {self.BATTERY_LOW}V)",
                            value=voltage
                        )
                    else:
                        self._clear_alert(device_id, "LOW_BATTERY")
                        
        except Exception as e:
            logger.error(f"Error checking battery voltage: {e}")
    
    def check_temperature(self):
        """Check for high temperature conditions"""
        query = f'''
        from(bucket: "{self.bucket}")
          |> range(start: -5m)
          |> filter(fn: (r) => r._measurement == "mqtt_consumer")
          |> filter(fn: (r) => r._field == "soil_temperature_c")
          |> last()
        '''
        
        try:
            result = self.query_api.query(query)
            for table in result:
                for record in table.records:
                    temp = record.get_value()
                    device_id = record.values.get('device_id', 'unknown')
                    
                    if temp > self.TEMP_HIGH:
                        self._trigger_alert(
                            device_id=device_id,
                            alert_type="HIGH_TEMPERATURE",
                            severity="warning",
                            message=f"Warning: Soil temperature at {temp:.1f}°C (threshold: {self.TEMP_HIGH}°C)",
                            value=temp
                        )
                    else:
                        self._clear_alert(device_id, "HIGH_TEMPERATURE")
                        
        except Exception as e:
            logger.error(f"Error checking temperature: {e}")
    
    def check_sensor_online(self):
        """Check if sensors are sending data (not offline)"""
        query = f'''
        from(bucket: "{self.bucket}")
          |> range(start: -{self.SENSOR_TIMEOUT_SECONDS}s)
          |> filter(fn: (r) => r._measurement == "mqtt_consumer")
          |> filter(fn: (r) => r._field == "soil_moisture_percent")
          |> group(columns: ["device_id"])
          |> last()
        '''
        
        try:
            result = self.query_api.query(query)
            if not result or len(result) == 0:
                # No data at all - sensor might be offline
                self._trigger_alert(
                    device_id="system",
                    alert_type="SENSOR_OFFLINE",
                    severity="critical",
                    message=f"Critical: No sensor data received in last {self.SENSOR_TIMEOUT_SECONDS} seconds",
                    value=0
                )
            else:
                # Check timestamp of last data
                for table in result:
                    for record in table.records:
                        device_id = record.values.get('device_id', 'unknown')
                        last_time = record.get_time()
                        time_diff = datetime.now(timezone.utc) - last_time
                        
                        if time_diff.total_seconds() > self.SENSOR_TIMEOUT_SECONDS:
                            self._trigger_alert(
                                device_id=device_id,
                                alert_type="SENSOR_OFFLINE",
                                severity="critical",
                                message=f"Critical: No data from sensor in {int(time_diff.total_seconds())} seconds",
                                value=time_diff.total_seconds()
                            )
                        else:
                            self._clear_alert(device_id, "SENSOR_OFFLINE")
                            
        except Exception as e:
            logger.error(f"Error checking sensor status: {e}")
    
    def _trigger_alert(self, device_id, alert_type, severity, message, value):
        """Trigger an alert and log to InfluxDB"""
        alert_key = f"{device_id}_{alert_type}"
        
        # Check if this alert is already active
        if alert_key in self.alert_state and self.alert_state[alert_key]:
            return  # Alert already active, don't spam
        
        # Log alert
        logger.warning(f"ALERT [{severity.upper()}] {device_id}: {message}")
        
        # Write alert to InfluxDB
        try:
            point = {
                "measurement": "alerts",
                "tags": {
                    "device_id": device_id,
                    "alert_type": alert_type,
                    "severity": severity
                },
                "fields": {
                    "message": message,
                    "value": float(value),
                    "active": True
                },
                "time": datetime.utcnow()
            }
            
            self.write_api.write(bucket=self.alert_bucket, org=self.org, record=point)
            self.alert_state[alert_key] = True
            
        except Exception as e:
            logger.error(f"Error writing alert to InfluxDB: {e}")
    
    def _clear_alert(self, device_id, alert_type):
        """Clear an alert when condition is resolved"""
        alert_key = f"{device_id}_{alert_type}"
        
        # Only log if alert was previously active
        if alert_key in self.alert_state and self.alert_state[alert_key]:
            logger.info(f"RESOLVED: {device_id} - {alert_type}")
            
            # Write resolution to InfluxDB
            try:
                point = {
                    "measurement": "alerts",
                    "tags": {
                        "device_id": device_id,
                        "alert_type": alert_type,
                        "severity": "resolved"
                    },
                    "fields": {
                        "message": f"{alert_type} condition resolved",
                        "value": 0.0,
                        "active": False
                    },
                    "time": datetime.utcnow()
                }
                
                self.write_api.write(bucket=self.alert_bucket, org=self.org, record=point)
                self.alert_state[alert_key] = False
                
            except Exception as e:
                logger.error(f"Error writing alert resolution to InfluxDB: {e}")
    
    def run_monitoring_cycle(self):
        """Run one complete monitoring cycle"""
        logger.debug("Running monitoring cycle...")
        
        self.check_soil_moisture()
        self.check_battery_voltage()
        self.check_temperature()
        self.check_sensor_online()
        
        logger.debug("Monitoring cycle complete")
    
    def run(self, interval=30):
        """Run alert system continuously"""
        logger.info(f"Alert system starting - check interval: {interval}s")
        logger.info(f"Monitoring thresholds:")
        logger.info(f"  - Soil moisture low: {self.MOISTURE_LOW}%")
        logger.info(f"  - Soil moisture critical: {self.MOISTURE_CRITICAL}%")
        logger.info(f"  - Battery low: {self.BATTERY_LOW}V")
        logger.info(f"  - Temperature high: {self.TEMP_HIGH}°C")
        logger.info(f"  - Sensor timeout: {self.SENSOR_TIMEOUT_SECONDS}s")
        
        try:
            while True:
                self.run_monitoring_cycle()
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("Alert system stopping...")
        finally:
            self.client.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='IoT Alert System')
    parser.add_argument('--url', default=os.getenv('INFLUXDB_URL', 'http://localhost:8086'),
                        help='InfluxDB URL')
    parser.add_argument('--token', default=os.getenv('INFLUXDB_TOKEN', 'your-super-secret-auth-token'),
                        help='InfluxDB authentication token')
    parser.add_argument('--org', default=os.getenv('INFLUXDB_ORG', 'smartfarm'),
                        help='InfluxDB organization')
    parser.add_argument('--bucket', default=os.getenv('INFLUXDB_BUCKET', 'soil_data'),
                        help='InfluxDB bucket to monitor')
    parser.add_argument('--alert-bucket', default=os.getenv('INFLUXDB_ALERT_BUCKET', 'alerts'),
                        help='InfluxDB bucket for alerts')
    parser.add_argument('--interval', type=int, default=30,
                        help='Check interval in seconds (default: 30)')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("=== IoT Alert System Starting ===")
    
    # Create alert system
    alert_system = AlertSystem(
        influxdb_url=args.url,
        token=args.token,
        org=args.org,
        bucket=args.bucket,
        alert_bucket=args.alert_bucket
    )
    
    # Run monitoring
    alert_system.run(interval=args.interval)


if __name__ == '__main__':
    main()
