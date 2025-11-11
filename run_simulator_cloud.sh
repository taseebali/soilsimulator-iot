#!/bin/bash
# Run the soil sensor simulator on the VM (cloud deployment)
# This script runs the simulator in the background so it continues after SSH disconnect

echo "=== Starting Soil Sensor Simulator on Cloud VM ==="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

# Check if paho-mqtt is installed
if ! python3 -c "import paho.mqtt.client" &> /dev/null; then
    echo "Installing paho-mqtt..."
    pip3 install paho-mqtt
fi

# Navigate to the project directory
cd ~/soilsimulator-iot || exit 1

# Kill any existing simulator processes
pkill -f "soil_sensor_simulator.py" 2>/dev/null

# Run the simulator in the background with nohup
# This keeps it running even after you disconnect from SSH
nohup python3 soil_sensor_simulator.py \
    --broker localhost \
    --port 1883 \
    --interval 60 \
    --verbose \
    > simulator.log 2>&1 &

SIMULATOR_PID=$!
echo "Simulator started with PID: $SIMULATOR_PID"
echo "Logs available at: ~/soilsimulator-iot/simulator.log"

# Wait a moment and check if it's running
sleep 2
if ps -p $SIMULATOR_PID > /dev/null; then
    echo "✓ Simulator is running successfully"
    echo ""
    echo "To view logs in real-time: tail -f ~/soilsimulator-iot/simulator.log"
    echo "To stop the simulator: pkill -f soil_sensor_simulator.py"
else
    echo "✗ Simulator failed to start. Check simulator.log for errors"
    exit 1
fi
