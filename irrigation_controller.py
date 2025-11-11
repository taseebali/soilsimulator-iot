#!/usr/bin/env python3
"""
Irrigation Controller - Automated irrigation control based on soil moisture
This actuator subscribes to sensor data and controls irrigation valves
"""

import os
import sys
import time
import json
import logging
import argparse
from datetime import datetime, timezone
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IrrigationController:
    """Automated irrigation controller based on soil moisture levels"""
    
    # Control thresholds
    MOISTURE_TARGET = 50.0  # Optimal moisture level
    MOISTURE_LOW = 35.0     # Start irrigation
    MOISTURE_HIGH = 65.0    # Stop irrigation
    
    # Irrigation settings
    MIN_IRRIGATION_DURATION = 60   # Minimum 1 minute
    MAX_IRRIGATION_DURATION = 600  # Maximum 10 minutes
    COOLDOWN_PERIOD = 900          # 15 minutes between irrigations
    
    def __init__(self, mqtt_broker, mqtt_port, mqtt_username=None, mqtt_password=None,
                 influxdb_url=None, influxdb_token=None, influxdb_org=None, influxdb_bucket=None):
        """Initialize irrigation controller"""
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_username = mqtt_username
        self.mqtt_password = mqtt_password
        
        # MQTT client
        self.client = mqtt.Client(client_id="irrigation_controller", clean_session=True)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        
        if mqtt_username and mqtt_password:
            self.client.username_pw_set(mqtt_username, mqtt_password)
        
        # Track valve states and last irrigation
        self.valve_states = {}  # {device_id: {'open': bool, 'opened_at': timestamp}}
        self.last_irrigation = {}  # {device_id: timestamp}
        
        # InfluxDB client (optional - for logging valve actions)
        self.influx_client = None
        self.write_api = None
        if influxdb_url and influxdb_token:
            self.influx_client = InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org)
            self.write_api = self.influx_client.write_api(write_options=SYNCHRONOUS)
            self.influx_org = influxdb_org
            self.influx_bucket = influxdb_bucket
            logger.info("InfluxDB logging enabled")
        
        self.connected = False
        logger.info("Irrigation controller initialized")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            self.connected = True
            logger.info(f"Connected to MQTT broker at {self.mqtt_broker}:{self.mqtt_port}")
            
            # Subscribe to sensor data topics
            client.subscribe("farm/+/sensors", qos=1)
            logger.info("Subscribed to sensor data topics: farm/+/sensors")
        else:
            logger.error(f"Failed to connect to MQTT broker. Return code: {rc}")
            self.connected = False
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker"""
        self.connected = False
        if rc != 0:
            logger.warning(f"Unexpected disconnection from MQTT broker. Return code: {rc}")
            logger.info("Attempting to reconnect...")
    
    def _on_message(self, client, userdata, msg):
        """Callback when a message is received"""
        try:
            # Parse sensor data
            payload = json.loads(msg.payload.decode())
            device_id = payload.get('device_id', 'unknown')
            moisture = payload.get('soil_moisture_percent')
            
            if moisture is None:
                return
            
            logger.debug(f"Received data from {device_id}: moisture={moisture:.1f}%")
            
            # Make irrigation decision
            self._make_irrigation_decision(device_id, moisture)
            
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON from topic {msg.topic}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def _make_irrigation_decision(self, device_id, moisture):
        """Decide whether to open/close irrigation valve"""
        current_time = time.time()
        
        # Initialize device state if needed
        if device_id not in self.valve_states:
            self.valve_states[device_id] = {'open': False, 'opened_at': None}
        
        valve = self.valve_states[device_id]
        
        # Check if valve is currently open
        if valve['open']:
            # Check if we should close the valve
            if moisture >= self.MOISTURE_HIGH:
                # Moisture is sufficient, close valve
                self._close_valve(device_id, reason="target_reached")
                logger.info(f"Valve closed for {device_id}: moisture reached {moisture:.1f}%")
            
            elif valve['opened_at'] and (current_time - valve['opened_at']) > self.MAX_IRRIGATION_DURATION:
                # Maximum irrigation time exceeded
                self._close_valve(device_id, reason="max_duration")
                logger.warning(f"Valve closed for {device_id}: max duration exceeded")
        
        else:
            # Valve is closed, check if we should open it
            if moisture < self.MOISTURE_LOW:
                # Check cooldown period
                last_irrigation = self.last_irrigation.get(device_id, 0)
                if (current_time - last_irrigation) > self.COOLDOWN_PERIOD:
                    # Open valve
                    duration = self._calculate_irrigation_duration(moisture)
                    self._open_valve(device_id, duration, moisture)
                    logger.info(f"Valve opened for {device_id}: moisture at {moisture:.1f}% (target: {self.MOISTURE_TARGET}%)")
                else:
                    remaining = int(self.COOLDOWN_PERIOD - (current_time - last_irrigation))
                    logger.debug(f"Cooldown active for {device_id}: {remaining}s remaining")
    
    def _calculate_irrigation_duration(self, current_moisture):
        """Calculate how long to irrigate based on moisture deficit"""
        moisture_deficit = self.MOISTURE_TARGET - current_moisture
        
        # Simple linear calculation: 1 minute per 5% deficit
        duration = int((moisture_deficit / 5.0) * 60)
        
        # Clamp to min/max values
        duration = max(self.MIN_IRRIGATION_DURATION, min(duration, self.MAX_IRRIGATION_DURATION))
        
        return duration
    
    def _open_valve(self, device_id, duration, moisture):
        """Open irrigation valve"""
        current_time = time.time()
        
        # Update valve state
        self.valve_states[device_id] = {
            'open': True,
            'opened_at': current_time
        }
        
        # Publish valve command to MQTT
        command = {
            'device_id': device_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'command': 'open_valve',
            'duration_seconds': duration,
            'reason': 'low_moisture',
            'current_moisture': moisture,
            'target_moisture': self.MOISTURE_TARGET
        }
        
        topic = f"farm/{device_id}/actuators/valve"
        self.client.publish(topic, json.dumps(command), qos=1)
        logger.info(f"Published valve OPEN command to {topic} (duration: {duration}s)")
        
        # Log to InfluxDB
        self._log_valve_action(device_id, 'open', duration, moisture)
        
        # Schedule automatic close
        # In production, this would be handled by a timer or scheduler
        # For now, we rely on moisture reaching target or max duration
    
    def _close_valve(self, device_id, reason="manual"):
        """Close irrigation valve"""
        # Calculate actual irrigation duration
        valve = self.valve_states[device_id]
        duration = 0
        if valve['opened_at']:
            duration = int(time.time() - valve['opened_at'])
        
        # Update valve state
        self.valve_states[device_id] = {
            'open': False,
            'opened_at': None
        }
        
        # Update last irrigation time
        self.last_irrigation[device_id] = time.time()
        
        # Publish valve command to MQTT
        command = {
            'device_id': device_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'command': 'close_valve',
            'reason': reason,
            'actual_duration_seconds': duration
        }
        
        topic = f"farm/{device_id}/actuators/valve"
        self.client.publish(topic, json.dumps(command), qos=1)
        logger.info(f"Published valve CLOSE command to {topic} (reason: {reason}, duration: {duration}s)")
        
        # Log to InfluxDB
        self._log_valve_action(device_id, 'close', duration, 0)
    
    def _log_valve_action(self, device_id, action, duration, moisture):
        """Log valve action to InfluxDB"""
        if not self.write_api:
            return
        
        try:
            point = {
                "measurement": "irrigation_control",
                "tags": {
                    "device_id": device_id,
                    "action": action
                },
                "fields": {
                    "valve_open": 1.0 if action == 'open' else 0.0,
                    "duration_seconds": float(duration),
                    "moisture_percent": float(moisture) if moisture else 0.0
                },
                "time": datetime.utcnow()
            }
            
            self.write_api.write(bucket=self.influx_bucket, org=self.influx_org, record=point)
            logger.debug(f"Logged valve {action} to InfluxDB")
            
        except Exception as e:
            logger.error(f"Error logging to InfluxDB: {e}")
    
    def connect(self):
        """Connect to MQTT broker"""
        try:
            logger.info(f"Connecting to MQTT broker at {self.mqtt_broker}:{self.mqtt_port}...")
            self.client.connect(self.mqtt_broker, self.mqtt_port, keepalive=60)
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return False
    
    def run(self):
        """Run the irrigation controller"""
        logger.info("=== Irrigation Controller Starting ===")
        logger.info(f"Control thresholds:")
        logger.info(f"  - Moisture target: {self.MOISTURE_TARGET}%")
        logger.info(f"  - Irrigation start: {self.MOISTURE_LOW}%")
        logger.info(f"  - Irrigation stop: {self.MOISTURE_HIGH}%")
        logger.info(f"  - Cooldown period: {self.COOLDOWN_PERIOD}s")
        
        if not self.connect():
            logger.error("Failed to establish initial connection. Exiting.")
            return
        
        try:
            # Start MQTT loop
            self.client.loop_forever()
        except KeyboardInterrupt:
            logger.info("Irrigation controller stopping...")
        finally:
            # Close all valves on shutdown
            for device_id in list(self.valve_states.keys()):
                if self.valve_states[device_id]['open']:
                    self._close_valve(device_id, reason="shutdown")
            
            self.client.disconnect()
            if self.influx_client:
                self.influx_client.close()
            logger.info("=== Irrigation Controller Stopped ===")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Irrigation Controller')
    parser.add_argument('--broker', default=os.getenv('MQTT_BROKER', 'localhost'),
                        help='MQTT broker address')
    parser.add_argument('--port', type=int, default=int(os.getenv('MQTT_PORT', '1883')),
                        help='MQTT broker port')
    parser.add_argument('--username', default=os.getenv('MQTT_USERNAME'),
                        help='MQTT username')
    parser.add_argument('--password', default=os.getenv('MQTT_PASSWORD'),
                        help='MQTT password')
    parser.add_argument('--influxdb-url', default=os.getenv('INFLUXDB_URL', 'http://localhost:8086'),
                        help='InfluxDB URL (optional)')
    parser.add_argument('--influxdb-token', default=os.getenv('INFLUXDB_TOKEN', 'your-super-secret-auth-token'),
                        help='InfluxDB token (optional)')
    parser.add_argument('--influxdb-org', default=os.getenv('INFLUXDB_ORG', 'smartfarm'),
                        help='InfluxDB organization')
    parser.add_argument('--influxdb-bucket', default=os.getenv('INFLUXDB_BUCKET', 'soil_data'),
                        help='InfluxDB bucket')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create controller
    controller = IrrigationController(
        mqtt_broker=args.broker,
        mqtt_port=args.port,
        mqtt_username=args.username,
        mqtt_password=args.password,
        influxdb_url=args.influxdb_url,
        influxdb_token=args.influxdb_token,
        influxdb_org=args.influxdb_org,
        influxdb_bucket=args.influxdb_bucket
    )
    
    # Run controller
    controller.run()


if __name__ == '__main__':
    main()
