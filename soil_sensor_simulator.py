#!/usr/bin/env python3
"""
Soil Sensor Simulator for Smart Agriculture IoT Project
Simulates soil moisture and environmental sensors, publishes data to MQTT broker.
"""
import paho.mqtt.client as mqtt
import json
import time
import random
import logging
import argparse
import os
import signal
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
running = True

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    global running
    logger.info("Shutdown signal received. Stopping sensor simulator...")
    running = False

def on_connect(client, userdata, flags, rc, properties=None):
    """Callback when client connects to broker"""
    if rc == 0:
        logger.info(f"Connected to MQTT broker successfully")
    else:
        logger.error(f"Failed to connect to MQTT broker. Return code: {rc}")

def on_disconnect(client, userdata, flags, rc, properties=None):
    """Callback when client disconnects from broker"""
    if rc != 0:
        logger.warning(f"Unexpected disconnection from MQTT broker. Return code: {rc}")
        logger.info("Attempting to reconnect...")

def on_publish(client, userdata, mid, reason_code=None, properties=None):
    """Callback when message is published"""
    logger.debug(f"Message {mid} published successfully")

def generate_sensor_data(device_id, field_name, base_moisture=45):
    """
    Generate realistic soil sensor data
    
    Args:
        device_id: Unique identifier for the sensor device
        field_name: Name of the field being monitored
        base_moisture: Base soil moisture level (default 45%)
    
    Returns:
        dict: Sensor data payload
    """
    moisture_variation = random.uniform(-5, 5)
    
    data = {
        "device_id": device_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "field_name": field_name,
        "soil_moisture_percent": round(base_moisture + moisture_variation, 2),
        "soil_temperature_c": round(random.uniform(18, 28), 1),
        "air_temperature_c": round(random.uniform(20, 32), 1),
        "air_humidity_percent": round(random.uniform(40, 70), 1),
        "battery_voltage": round(random.uniform(3.6, 4.2), 2),
        "location": {"lat": 52.5200, "lon": 13.4050}  # Berlin coordinates
    }
    return data

def main():
    """Main function to run the sensor simulator"""
    global running
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Soil Sensor Simulator for Smart Agriculture')
    parser.add_argument('--broker', type=str, 
                       default=os.getenv('MQTT_BROKER', 'localhost'),
                       help='MQTT broker hostname or IP (default: localhost, env: MQTT_BROKER)')
    parser.add_argument('--port', type=int,
                       default=int(os.getenv('MQTT_PORT', '1883')),
                       help='MQTT broker port (default: 1883, env: MQTT_PORT)')
    parser.add_argument('--topic', type=str,
                       default=os.getenv('MQTT_TOPIC', 'farm/field_01/sensors'),
                       help='MQTT topic to publish to (default: farm/field_01/sensors, env: MQTT_TOPIC)')
    parser.add_argument('--interval', type=int,
                       default=int(os.getenv('PUBLISH_INTERVAL', '120')),
                       help='Publish interval in seconds (default: 120, env: PUBLISH_INTERVAL)')
    parser.add_argument('--device-id', type=str,
                       default=os.getenv('DEVICE_ID', 'field_sensor_01'),
                       help='Device ID (default: field_sensor_01, env: DEVICE_ID)')
    parser.add_argument('--field-name', type=str,
                       default=os.getenv('FIELD_NAME', 'Field A - Tomatoes'),
                       help='Field name (default: Field A - Tomatoes, env: FIELD_NAME)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Dry run mode - print data without publishing to MQTT')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("=== Soil Sensor Simulator Starting ===")
    logger.info(f"MQTT Broker: {args.broker}:{args.port}")
    logger.info(f"MQTT Topic: {args.topic}")
    logger.info(f"Device ID: {args.device_id}")
    logger.info(f"Field Name: {args.field_name}")
    logger.info(f"Publish Interval: {args.interval} seconds")
    logger.info(f"Dry Run Mode: {args.dry_run}")
    
    client = None
    
    if not args.dry_run:
        # Create MQTT client with callback API version 2
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_publish = on_publish
        
        # Enable automatic reconnection
        client.reconnect_delay_set(min_delay=1, max_delay=120)
        
        try:
            logger.info(f"Connecting to MQTT broker at {args.broker}:{args.port}...")
            client.connect(args.broker, args.port, 60)
            client.loop_start()  # Start network loop in background thread
            time.sleep(2)  # Give time for connection to establish
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            logger.error("Please check broker address and ensure it's running")
            return 1
    
    try:
        message_count = 0
        while running:
            # Generate sensor data
            sensor_data = generate_sensor_data(
                device_id=args.device_id,
                field_name=args.field_name
            )
            payload = json.dumps(sensor_data)
            
            if args.dry_run:
                # Dry run - just print the data
                print(f"[DRY RUN] Would publish to {args.topic}: {payload}")
            else:
                # Publish to MQTT broker
                result = client.publish(args.topic, payload, qos=1)
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    message_count += 1
                    logger.info(f"Published message #{message_count}: {payload}")
                else:
                    logger.error(f"Failed to publish message. Error code: {result.rc}")
            
            # Wait for the specified interval
            time.sleep(args.interval)
            
    except Exception as e:
        logger.error(f"Error in main loop: {e}")
        return 1
    finally:
        if client and not args.dry_run:
            logger.info("Disconnecting from MQTT broker...")
            client.loop_stop()
            client.disconnect()
        
        logger.info(f"=== Soil Sensor Simulator Stopped. Total messages: {message_count} ===")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())