#!/bin/bash
# Complete setup script for enhanced IoT system on VM
# Run this on your GCP VM after cloning the repository

set -e  # Exit on any error

echo "================================================"
echo "  Smart Agriculture IoT - Complete Setup"
echo "  Enhanced Edition with Security & Automation"
echo "================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "soil_sensor_simulator.py" ]; then
    echo "ERROR: Must run from soilsimulator-iot directory"
    exit 1
fi

# Step 1: Install dependencies
echo "Step 1/7: Installing Python dependencies..."
pip3 install --upgrade paho-mqtt influxdb-client

# Step 2: Create InfluxDB buckets
echo ""
echo "Step 2/7: Creating InfluxDB buckets..."
docker exec influxdb influx bucket create \
    --name alerts \
    --org smartfarm \
    --token your-super-secret-auth-token \
    --retention 30d 2>/dev/null || echo "  ✓ Alerts bucket exists"

# Step 3: Make scripts executable
echo ""
echo "Step 3/7: Making scripts executable..."
chmod +x *.sh

# Step 4: Start alert system
echo ""
echo "Step 4/7: Starting alert monitoring system..."
pkill -f alert_system.py 2>/dev/null || true
nohup python3 alert_system.py \
    --url http://localhost:8086 \
    --token your-super-secret-auth-token \
    --org smartfarm \
    --bucket soil_data \
    --alert-bucket alerts \
    --interval 30 \
    --verbose \
    > alerts.log 2>&1 &

ALERT_PID=$!
sleep 2
if ps -p $ALERT_PID > /dev/null; then
    echo "  ✓ Alert system running (PID: $ALERT_PID)"
else
    echo "  ✗ Alert system failed to start"
fi

# Step 5: Start irrigation controller
echo ""
echo "Step 5/7: Starting irrigation controller..."
pkill -f irrigation_controller.py 2>/dev/null || true
nohup python3 irrigation_controller.py \
    --broker localhost \
    --port 1883 \
    --influxdb-url http://localhost:8086 \
    --influxdb-token your-super-secret-auth-token \
    --influxdb-org smartfarm \
    --influxdb-bucket soil_data \
    --verbose \
    > irrigation.log 2>&1 &

IRRIGATION_PID=$!
sleep 2
if ps -p $IRRIGATION_PID > /dev/null; then
    echo "  ✓ Irrigation controller running (PID: $IRRIGATION_PID)"
else
    echo "  ✗ Irrigation controller failed to start"
fi

# Step 6: Start simulator
echo ""
echo "Step 6/7: Starting soil sensor simulator..."
pkill -f soil_sensor_simulator.py 2>/dev/null || true
nohup python3 soil_sensor_simulator.py \
    --broker localhost \
    --port 1883 \
    --interval 60 \
    --verbose \
    > simulator.log 2>&1 &

SIMULATOR_PID=$!
sleep 2
if ps -p $SIMULATOR_PID > /dev/null; then
    echo "  ✓ Simulator running (PID: $SIMULATOR_PID)"
else
    echo "  ✗ Simulator failed to start"
fi

# Step 7: Verify system
echo ""
echo "Step 7/7: Verifying system health..."

# Check Docker containers
CONTAINERS=$(docker ps --format '{{.Names}}' | wc -l)
echo "  ✓ Docker containers running: $CONTAINERS/4"

# Check MQTT
docker exec mqtt_broker mosquitto_pub -h localhost -t 'test' -m 'hello' > /dev/null 2>&1 && \
    echo "  ✓ MQTT broker responding" || \
    echo "  ✗ MQTT broker not responding"

# Check InfluxDB
docker exec influxdb influx ping > /dev/null 2>&1 && \
    echo "  ✓ InfluxDB responding" || \
    echo "  ✗ InfluxDB not responding"

# Get external IP
EXTERNAL_IP=$(curl -s ifconfig.me)

echo ""
echo "================================================"
echo "  🎉 Setup Complete!"
echo "================================================"
echo ""
echo "Running Services:"
echo "  ✓ MQTT Broker (mosquitto)"
echo "  ✓ Time-series Database (influxdb)"
echo "  ✓ Data Collector (telegraf)"
echo "  ✓ Dashboard (grafana)"
echo "  ✓ Alert System (alert_system.py)"
echo "  ✓ Irrigation Controller (irrigation_controller.py)"
echo "  ✓ Sensor Simulator (soil_sensor_simulator.py)"
echo ""
echo "Access URLs:"
echo "  📊 Grafana:  http://${EXTERNAL_IP}:3000"
echo "     Login: admin / admin"
echo ""
echo "  📈 InfluxDB: http://${EXTERNAL_IP}:8086"
echo "     Token: your-super-secret-auth-token"
echo ""
echo "Monitor Logs:"
echo "  tail -f alerts.log          # Alert system"
echo "  tail -f irrigation.log      # Irrigation controller"
echo "  tail -f simulator.log       # Sensor simulator"
echo ""
echo "View MQTT Messages:"
echo "  # Sensor data"
echo "  docker exec mqtt_broker mosquitto_sub -h localhost -t 'farm/#' -v"
echo ""
echo "  # Actuator commands"
echo "  docker exec mqtt_broker mosquitto_sub -h localhost -t 'farm/+/actuators/#' -v"
echo ""
echo "Check System Status:"
echo "  ps aux | grep -E 'alert_system|irrigation_controller|soil_sensor_simulator'"
echo ""
echo "Stop All Services:"
echo "  pkill -f 'alert_system|irrigation_controller|soil_sensor_simulator'"
echo ""
echo "Optional Enhancements:"
echo "  🔒 Enable MQTT security: ./enable_mqtt_security.sh"
echo "  📊 Add actuator panels to Grafana: see GRAFANA_ACTUATOR_PANELS.md"
echo ""
echo "Documentation:"
echo "  📖 ENHANCED_FEATURES_GUIDE.md - Complete feature guide"
echo "  📖 RUNNING_SIMULATOR_ON_VM.md - Simulator management"
echo "  📖 CLOUD_VM_SETUP.md - Cloud deployment"
echo ""
echo "================================================"
