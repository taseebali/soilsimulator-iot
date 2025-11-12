#!/bin/bash

# Restart Services Script for VM
# Run this after VM restart to restore all services

echo "🔄 Restarting IoT System Services..."

# Navigate to project directory
cd ~/soilsimulator-iot || { echo "❌ Project directory not found"; exit 1; }

# Verify Docker containers are running
echo "📦 Checking Docker containers..."
docker ps

# Check if historical data exists
echo ""
echo "📊 Verifying historical data..."
docker exec influxdb influx query 'from(bucket:"soil_data") |> range(start:-24h) |> limit(n:5)' --org smartfarm --token your-super-secret-auth-token

# Stop any existing Python processes (cleanup)
echo ""
echo "🧹 Cleaning up old processes..."
pkill -f soil_sensor_simulator.py 2>/dev/null
pkill -f irrigation_controller.py 2>/dev/null
pkill -f alert_system.py 2>/dev/null
sleep 2

# Start Soil Sensor Simulator
echo ""
echo "🌱 Starting Soil Sensor Simulator..."
nohup python3 soil_sensor_simulator.py \
    --broker localhost \
    --username iot_soil \
    --password admin \
    --interval 60 \
    --verbose > simulator.log 2>&1 &
echo "  PID: $!"

sleep 2

# Start Irrigation Controller
echo ""
echo "💧 Starting Irrigation Controller..."
nohup python3 irrigation_controller.py \
    --broker localhost \
    --username iot_soil \
    --password admin \
    --influxdb-url http://localhost:8086 \
    --influxdb-token your-super-secret-auth-token \
    --verbose > irrigation.log 2>&1 &
echo "  PID: $!"

sleep 2

# Start Alert System
echo ""
echo "🚨 Starting Alert System..."
nohup python3 alert_system.py \
    --url http://localhost:8086 \
    --token your-super-secret-auth-token \
    --org smartfarm \
    --bucket soil_data \
    --verbose > alerts.log 2>&1 &
echo "  PID: $!"

sleep 3

# Verify all services are running
echo ""
echo "✅ Service Status:"
ps aux | grep -E 'soil_sensor|irrigation_controller|alert_system' | grep -v grep

# Show recent logs
echo ""
echo "📋 Recent Simulator Log:"
tail -n 5 simulator.log 2>/dev/null || echo "  No logs yet, wait a moment..."

echo ""
echo "📋 Recent Irrigation Log:"
tail -n 5 irrigation.log 2>/dev/null || echo "  No logs yet, wait a moment..."

echo ""
echo "📋 Recent Alerts Log:"
tail -n 5 alerts.log 2>/dev/null || echo "  No logs yet, wait a moment..."

echo ""
echo "🎉 System restart complete!"
echo "📊 Grafana Dashboard: http://$(curl -s ifconfig.me):3000"
echo "   Username: admin"
echo "   Password: admin"
echo ""
echo "💡 To check logs anytime:"
echo "   tail -f simulator.log"
echo "   tail -f irrigation.log"
echo "   tail -f alerts.log"
