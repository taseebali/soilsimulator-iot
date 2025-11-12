# Smart Agriculture - IoT Soil Monitoring System 🌱

A complete cloud-based IoT solution for smart agriculture with automated irrigation control, real-time monitoring, and intelligent alerting.

## System Overview

### Problem
Farmers waste water and lose crops due to inefficient irrigation - either overwatering or underwatering fields without real-time data.

### Solution
Automated IoT system that monitors soil conditions 24/7 and controls irrigation based on real-time data, deployed entirely in the cloud.

## Architecture

**Data Flow:** Sensors → MQTT → Telegraf → InfluxDB → Grafana
**Control Loop:** InfluxDB → Controller → MQTT → Actuators → Sensors

### Components
- **Sensor Simulator**: Python script generating realistic soil data (moisture, temperature, humidity, rainfall)
- **MQTT Broker** (Mosquitto): Secure message broker with authentication
- **Telegraf**: Data collector forwarding MQTT messages to InfluxDB
- **InfluxDB**: Time-series database storing sensor readings and alerts
- **Grafana**: Real-time dashboard with 12 visualization panels
- **Irrigation Controller**: Automated valve control based on moisture thresholds
- **Alert System**: Monitors critical conditions (low moisture, battery, temperature, sensor offline)

## 📁 Project Structure

```
soilsimulator-iot/
├── soil_sensor_simulator.py       # Sensor simulator with closed-loop feedback
├── irrigation_controller.py       # Automated irrigation control logic
├── alert_system.py                # Real-time monitoring and alerting
├── requirements.txt               # Python dependencies
├── docker/
│   ├── docker-compose.yml         # 4 services: Mosquitto, InfluxDB, Telegraf, Grafana
│   └── mosquitto/config/
│       └── mosquitto.conf         # MQTT broker with authentication
├── telegraf/
│   └── telegraf.conf              # MQTT → InfluxDB data pipeline
└── grafana/
    └── soil_monitoring_dashboard.json  # Enhanced 12-panel dashboard
```

## 🚀 Quick Start

### Cloud Deployment (GCP VM)

**Prerequisites:**
- GCP account with VM instance
- Docker installed on VM
- Python 3.8+

**1. Deploy Docker Stack on VM:**
```bash
cd ~/soilsimulator-iot
docker compose -f docker/docker-compose.yml up -d
```

**2. Start All Services:**
```bash
# Sensor simulator
nohup python3 soil_sensor_simulator.py --broker localhost --username iot_soil --password admin --interval 60 --verbose > simulator.log 2>&1 &

# Irrigation controller
nohup python3 irrigation_controller.py --broker localhost --username iot_soil --password admin --influxdb-url http://localhost:8086 --influxdb-token your-super-secret-auth-token --verbose > irrigation.log 2>&1 &

# Alert system
nohup python3 alert_system.py --url http://localhost:8086 --token your-super-secret-auth-token --org smartfarm --bucket soil_data --verbose > alerts.log 2>&1 &
```

**3. Access Grafana:**
```
http://YOUR_VM_IP:3000
Username: admin
Password: admin
```

**4. Import Dashboard:**
- Go to Dashboards → Import
- Upload `grafana/soil_monitoring_dashboard.json`
- Select `influxdb_datasource`

## 🔧 Configuration

### MQTT Authentication
- **Username**: `iot_soil`
- **Password**: `admin`

### InfluxDB Settings
- **URL**: `http://localhost:8086`
- **Organization**: `smartfarm`
- **Bucket**: `soil_data` (sensor data), `alerts` (system alerts)
- **Token**: `your-super-secret-auth-token`

### Irrigation Thresholds
Edit `irrigation_controller.py` to adjust:
- **Low threshold**: 35% (opens valve)
- **High threshold**: 65% (closes valve)
- **Cooldown**: 900 seconds

---

## 📊 Data Format

The simulator publishes JSON messages to MQTT with the following structure:

```json
{
  "device_id": "field_sensor_01",
  "timestamp": "2025-11-06T13:56:57.335483Z",
  "field_name": "Field A - Tomatoes",
  "soil_moisture_percent": 44.49,
  "soil_temperature_c": 26.8,
  "air_temperature_c": 26.8,
  "air_humidity_percent": 45.9,
  "battery_voltage": 3.78,
  "location": {
    "lat": 52.52,
    "lon": 13.405
  }
}
```



---

## 🛠️ Troubleshooting

### Services Not Running After VM Restart
```bash
# Restart Docker stack
cd ~/soilsimulator-iot
docker compose -f docker/docker-compose.yml restart

# Restart Python services (see Quick Start section for full commands)
```

### No Data in Grafana
- Check Telegraf logs: `docker logs telegraf`
- Verify MQTT credentials in `telegraf/telegraf.conf`
- Ensure Python services are running: `ps aux | grep python`

### Closed-Loop Irrigation Not Working
- Check simulator is receiving valve commands: `tail -f simulator.log`
- Verify controller is publishing: `tail -f irrigation.log`
- Ensure both services use same MQTT broker and credentials

##  License

Educational IoT demonstration project.
- Add authentication/security layers

---

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review Docker logs
3. Verify network connectivity
4. Consult official documentation:
   - [Paho MQTT Python](https://eclipse.dev/paho/index.php?page=clients/python/docs/index.php)
   - [Telegraf](https://docs.influxdata.com/telegraf/)
   - [InfluxDB](https://docs.influxdata.com/influxdb/)
   - [Grafana](https://grafana.com/docs/)

---

**Happy Farming! 🚜🌾**
