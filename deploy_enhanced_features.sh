#!/bin/bash
# Deploy enhanced features on the VM: security, alerts, and irrigation controller

echo "=== Deploying Enhanced IoT Features ==="

# Check if running on VM
if [ ! -d "$HOME/soilsimulator-iot" ]; then
    echo "ERROR: Project directory not found. Please clone the repo first:"
    echo "  git clone https://github.com/taseebali/soilsimulator-iot.git"
    exit 1
fi

cd ~/soilsimulator-iot

# Check if Docker is running
if ! docker ps > /dev/null 2>&1; then
    echo "ERROR: Docker is not running"
    exit 1
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install --upgrade paho-mqtt influxdb-client

# Create alerts bucket in InfluxDB
echo ""
echo "Creating alerts bucket in InfluxDB..."
docker exec influxdb influx bucket create \
    --name alerts \
    --org smartfarm \
    --token your-super-secret-auth-token \
    --retention 30d 2>/dev/null || echo "  (Bucket may already exist)"

# Make scripts executable
chmod +x enable_mqtt_security.sh
chmod +x run_simulator_cloud.sh

echo ""
echo "=== Enhanced Features Ready ==="
echo ""
echo "Next steps:"
echo ""
echo "1. ENABLE MQTT SECURITY (Optional but recommended):"
echo "   ./enable_mqtt_security.sh"
echo "   Then update simulator with: --username iot_user --password YOUR_PASSWORD"
echo ""
echo "2. START ALERT SYSTEM:"
echo "   nohup python3 alert_system.py --verbose > alerts.log 2>&1 &"
echo ""
echo "3. START IRRIGATION CONTROLLER:"
echo "   nohup python3 irrigation_controller.py --verbose > irrigation.log 2>&1 &"
echo ""
echo "4. VIEW LOGS:"
echo "   tail -f alerts.log"
echo "   tail -f irrigation.log"
echo ""
echo "5. CHECK RUNNING PROCESSES:"
echo "   ps aux | grep -E 'alert_system|irrigation_controller|soil_sensor'"
echo ""
echo "6. UPDATE GRAFANA DASHBOARD:"
echo "   Import the updated dashboard JSON that includes actuator panels"
echo ""
