#!/bin/bash
# Enable MQTT authentication for Mosquitto broker
# Run this script on your VM to secure MQTT access

echo "=== Enabling MQTT Security ==="

# Navigate to mosquitto config directory
MQTT_CONFIG_DIR="$HOME/soilsimulator-iot/docker/mosquitto/config"

# Backup original config
if [ -f "$MQTT_CONFIG_DIR/mosquitto.conf" ]; then
    cp "$MQTT_CONFIG_DIR/mosquitto.conf" "$MQTT_CONFIG_DIR/mosquitto.conf.backup"
    echo "✓ Backed up original config"
fi

# Check if security is already enabled
if grep -q "allow_anonymous false" "$MQTT_CONFIG_DIR/mosquitto.conf" 2>/dev/null; then
    echo "⚠ Security already enabled"
    exit 0
fi

# Add authentication settings to mosquitto.conf
cat >> "$MQTT_CONFIG_DIR/mosquitto.conf" << EOF

# Security Settings
allow_anonymous false
password_file /mosquitto/config/passwd
EOF

echo "✓ Updated mosquitto.conf with authentication settings"

# Create password file with default user
echo "Creating MQTT user credentials..."
echo ""
echo "Enter username for MQTT (default: iot_user):"
read -r MQTT_USER
MQTT_USER=${MQTT_USER:-iot_user}
MQTT_USER=${admin}
echo "Enter password for MQTT user:"
read -rs MQTT_PASSWORD

# Create password file using docker exec
docker exec mqtt_broker mosquitto_passwd -c -b /mosquitto/config/passwd "$MQTT_USER" "$MQTT_PASSWORD"

if [ $? -eq 0 ]; then
    echo "✓ Created MQTT user: $MQTT_USER"
else
    echo "✗ Failed to create MQTT user"
    exit 1
fi

# Restart mosquitto to apply changes
echo ""
echo "Restarting MQTT broker..."
docker restart mqtt_broker

# Wait for broker to restart
sleep 3

# Test connection
echo ""
echo "Testing MQTT authentication..."
docker exec mqtt_broker mosquitto_sub -h localhost -t 'test' -u "$MQTT_USER" -P "$MQTT_PASSWORD" -C 1 &
SUBSCRIBE_PID=$!
sleep 1
docker exec mqtt_broker mosquitto_pub -h localhost -t 'test' -m 'auth_test' -u "$MQTT_USER" -P "$MQTT_PASSWORD"
wait $SUBSCRIBE_PID 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✓ MQTT authentication working correctly"
else
    echo "✗ MQTT authentication test failed"
    exit 1
fi

echo ""
echo "=== MQTT Security Enabled Successfully ==="
echo ""
echo "IMPORTANT: Update your simulators and controllers with these credentials:"
echo "  Username: $MQTT_USER"
echo "  Password: [your password]"
echo ""
echo "To add more users: docker exec mqtt_broker mosquitto_passwd -b /mosquitto/config/passwd <username> <password>"
echo "To remove security: restore backup with: cp $MQTT_CONFIG_DIR/mosquitto.conf.backup $MQTT_CONFIG_DIR/mosquitto.conf"
