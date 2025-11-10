# Cloud Deployment Quick Reference

## 🚀 Running Sensor Simulator in Cloud Mode

### Quick Start

```powershell
# Set your GCP VM IP (do this once)
$env:GCP_VM_IP = "34.179.141.137"

# Run simulator connected to cloud
.\run_cloud.ps1
```

### Alternative Methods

#### Method 1: Using run_cloud.ps1 script
```powershell
# With IP as parameter
.\run_cloud.ps1 34.179.141.137

# With custom settings
.\run_cloud.ps1 -BrokerIP "34.179.141.137" -Interval 60 -DeviceId "field_02" -FieldName "Field B - Corn"
```

#### Method 2: Using environment variables
```powershell
$env:MQTT_BROKER = "34.179.141.137"
$env:PUBLISH_INTERVAL = "120"
python soil_sensor_simulator.py
```

#### Method 3: Using command-line arguments
```powershell
python soil_sensor_simulator.py --broker 34.179.141.137 --interval 120 --verbose
```

---

## 📋 Pre-Deployment Checklist

### On Your GCP VM:

1. **Deploy Docker Stack**
```bash
# SSH into your GCP VM
ssh user@YOUR_GCP_VM_IP

# Create project directory
mkdir -p ~/soil-monitoring
cd ~/soil-monitoring

# Copy files from local machine
# (On your local machine in PowerShell)
scp -r docker/ user@YOUR_GCP_VM_IP:~/soil-monitoring/
scp -r telegraf/ user@YOUR_GCP_VM_IP:~/soil-monitoring/

# Back on GCP VM, start services
cd ~/soil-monitoring/docker
docker-compose up -d
```

2. **Verify Services Running**
```bash
docker-compose ps

# Should show:
# - mqtt_broker (running)
# - influxdb (running)
# - telegraf (running)
# - grafana (running)
```

3. **Check Mosquitto Logs**
```bash
docker logs mqtt_broker --tail 20
```

### Configure GCP Firewall:

```bash
# Allow MQTT (port 1883)
gcloud compute firewall-rules create allow-mqtt \
    --allow tcp:1883 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow MQTT broker access"

# Allow Grafana (port 3000)
gcloud compute firewall-rules create allow-grafana \
    --allow tcp:3000 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow Grafana dashboard access"

# Allow InfluxDB (port 8086) - optional
gcloud compute firewall-rules create allow-influxdb \
    --allow tcp:8086 \
    --source-ranges YOUR_IP/32 \
    --description "Allow InfluxDB access"
```

### Test Connectivity:

```powershell
# From your local machine
Test-NetConnection -ComputerName YOUR_GCP_VM_IP -Port 1883
Test-NetConnection -ComputerName YOUR_GCP_VM_IP -Port 3000
```

---

## 🔧 Running Multiple Sensors (Multi-Field)

### Start 3 sensors for different fields:

```powershell
# Terminal 1 - Field A (Tomatoes)
.\run_cloud.ps1 -DeviceId "field_sensor_01" -FieldName "Field A - Tomatoes"

# Terminal 2 - Field B (Corn)
.\run_cloud.ps1 -DeviceId "field_sensor_02" -FieldName "Field B - Corn"

# Terminal 3 - Field C (Lettuce)
.\run_cloud.ps1 -DeviceId "field_sensor_03" -FieldName "Field C - Lettuce"
```

---

## 📊 Accessing Cloud Dashboard

### Grafana Dashboard:
```
URL: http://YOUR_GCP_VM_IP:3000
Username: admin
Password: admin
```

### InfluxDB UI:
```
URL: http://YOUR_GCP_VM_IP:8086
Username: admin
Password: smartfarm2025
Organization: smartfarm
```

---

## 🐛 Troubleshooting

### Problem: Cannot connect to broker

**Check 1: VM is running**
```bash
gcloud compute instances list
```

**Check 2: Firewall rules exist**
```bash
gcloud compute firewall-rules list | grep -E "mqtt|grafana"
```

**Check 3: Mosquitto is running on VM**
```bash
ssh user@YOUR_GCP_VM_IP
docker logs mqtt_broker --tail 50
```

**Check 4: Test from VM itself**
```bash
# On the VM
docker exec mqtt_broker mosquitto_sub -h localhost -t "farm/#" -v
```

### Problem: Simulator connects but no data in Grafana

**Check Telegraf logs:**
```bash
# On GCP VM
docker logs telegraf --tail 50
```

**Check InfluxDB has data:**
```bash
docker exec influxdb influx query 'from(bucket:"soil_data") |> range(start: -10m) |> limit(n:5)' --org smartfarm --token your-super-secret-auth-token
```

### Problem: Port 1883 unreachable

**Test with telnet (if available):**
```powershell
Test-NetConnection -ComputerName YOUR_GCP_VM_IP -Port 1883
```

**Or use MQTT test tool:**
```powershell
# Install mosquitto client
choco install mosquitto

# Test publish
mosquitto_pub -h YOUR_GCP_VM_IP -t test/topic -m "hello"
```

---

## 🔐 Security Considerations (Production)

### Enable TLS/SSL for MQTT:

1. Generate certificates on GCP VM
2. Update `mosquitto.conf`:
```conf
listener 1883
allow_anonymous false
password_file /mosquitto/config/passwd

listener 8883
allow_anonymous false
password_file /mosquitto/config/passwd
cafile /mosquitto/config/ca.crt
certfile /mosquitto/config/server.crt
keyfile /mosquitto/config/server.key
```

3. Update simulator to use SSL:
```powershell
python soil_sensor_simulator.py --broker YOUR_GCP_VM_IP --port 8883 --use-ssl
```

### Create MQTT users:
```bash
# On GCP VM
docker exec mqtt_broker mosquitto_passwd -c /mosquitto/config/passwd iot_device
```

---

## ☁️ Adding BigQuery Integration

Follow steps in `CLOUD_INTEGRATION.md`:

1. Create BigQuery dataset and table
2. Set up service account
3. Update `telegraf.conf` with BigQuery output
4. Restart Telegraf

---

## 📝 Quick Command Reference

```powershell
# Run locally
.\run_local.ps1

# Run with cloud
.\run_cloud.ps1 YOUR_GCP_VM_IP

# Run with verbose logging
python soil_sensor_simulator.py --broker YOUR_GCP_VM_IP --verbose

# Dry run (test without publishing)
python soil_sensor_simulator.py --broker YOUR_GCP_VM_IP --dry-run

# Check what's running
docker ps

# View logs
docker logs mqtt_broker -f
docker logs telegraf -f

# Stop everything
docker-compose down
```

---

## 🎯 Deployment Modes Summary

| Mode | Broker | Use Case | Command |
|------|--------|----------|---------|
| **Local** | localhost | Development/Testing | `.\run_local.ps1` |
| **Cloud** | GCP VM IP | Demo/Production | `.\run_cloud.ps1 VM_IP` |
| **Hybrid** | Both | Multi-site testing | Run multiple simulators |

---

## 📞 Need Help?

1. Check logs: `docker logs <container_name>`
2. Test connectivity: `Test-NetConnection`
3. Verify firewall rules: `gcloud compute firewall-rules list`
4. Check VM status: `gcloud compute instances list`

For detailed cloud integration (Pub/Sub, BigQuery, etc.), see `CLOUD_INTEGRATION.md`
