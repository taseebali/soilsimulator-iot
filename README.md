# Smart Agriculture - Soil Monitoring IoT Project 🌱

A complete IoT solution for smart agriculture that simulates soil moisture sensors and provides real-time monitoring through a cloud-based dashboard.

## Problem Statement

Farmers often over-water or under-water crops due to lack of real-time soil moisture data, leading to:
- Water waste (expensive/scarce resource)
- Reduced crop yields
- Inefficient resource management

## Solution Architecture

### Edge (IoT)
- **Soil moisture sensors** (simulated via Python script)
- **MQTT protocol** for lightweight, efficient data transmission
- Real-time sensor data: soil moisture, temperature, humidity, battery voltage

### Cloud Components
- **Mosquitto**: MQTT broker for message queuing
- **Telegraf**: Data collection and forwarding agent
- **InfluxDB**: Time-series database for sensor data storage
- **Grafana**: Real-time visualization dashboard
- **(Optional) Google Cloud**: BigQuery, Pub/Sub for advanced analytics

---

## 📁 Project Structure

```
Soil Simulator/
├── soil_sensor_simulator.py    # Python sensor simulator
├── requirements.txt             # Python dependencies
├── docker/
│   ├── docker-compose.yml      # Docker orchestration
│   └── mosquitto/
│       ├── config/
│       │   └── mosquitto.conf  # MQTT broker config
│       ├── data/               # MQTT persistence
│       └── log/                # MQTT logs
└── telegraf/
    └── telegraf.conf           # Telegraf configuration
```

---

## 🚀 Quick Start Guide

### Prerequisites

1. **Python 3.8+** installed
2. **Docker Desktop** installed and running
3. **(Optional) Google Cloud SDK** for cloud integration

### Step 1: Install Python Dependencies

```powershell
# Navigate to project directory
cd "C:\Development\IoT\Soil Simulator"

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Start the Docker Stack

```powershell
# Navigate to docker directory
cd docker

# Start all services (Mosquitto, InfluxDB, Telegraf, Grafana)
docker-compose up -d

# Verify all containers are running
docker-compose ps
```

**Services will be available at:**
- **Mosquitto (MQTT)**: `localhost:1883`
- **InfluxDB**: `http://localhost:8086`
- **Grafana**: `http://localhost:3000` (admin/admin)

### Step 3: Run the Sensor Simulator

#### Option A: Using Your GCP VM Broker (Current Setup)

```powershell
# From project root (with .venv activated)
python soil_sensor_simulator.py
```

This will publish to your GCP VM broker at `34.179.141.137`.

#### Option B: Using Local Mosquitto Broker

```powershell
python soil_sensor_simulator.py --broker localhost
```

#### Option C: Dry Run Mode (Test Without Publishing)

```powershell
python soil_sensor_simulator.py --dry-run
```

#### Option D: Custom Configuration

```powershell
# Custom broker, faster interval, different field
python soil_sensor_simulator.py --broker 192.168.1.100 --interval 30 --field-name "Field B - Corn"
```

### Step 4: Configure InfluxDB (First Time Only)

1. Open InfluxDB UI: `http://localhost:8086`
2. Login with:
   - **Username**: `admin`
   - **Password**: `smartfarm2025`
3. Verify the `soil_data` bucket exists
4. Copy the admin token: `your-super-secret-auth-token`

### Step 5: Create Grafana Dashboard

1. Open Grafana: `http://localhost:3000`
2. Login (default: `admin`/`admin`)
3. Add InfluxDB as a data source:
   - Go to **Configuration → Data Sources → Add data source**
   - Select **InfluxDB**
   - Configure:
     - **Query Language**: Flux
     - **URL**: `http://influxdb:8086`
     - **Organization**: `smartfarm`
     - **Token**: `your-super-secret-auth-token`
     - **Default Bucket**: `soil_data`
   - Click **Save & Test**

4. Create a new dashboard:
   - **+ → Dashboard → Add new panel**
   - Use Flux queries to visualize data:

```flux
from(bucket: "soil_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "mqtt_consumer")
  |> filter(fn: (r) => r._field == "soil_moisture_percent")
```

**Suggested Panels:**
- **Soil Moisture** (gauge or time series)
- **Soil Temperature** (time series)
- **Air Temperature & Humidity** (multi-series)
- **Battery Voltage** (gauge with thresholds)

---

## 🔧 Simulator Configuration Options

The sensor simulator supports multiple configuration methods:

### Command-Line Arguments

```powershell
python soil_sensor_simulator.py [OPTIONS]

Options:
  --broker TEXT        MQTT broker hostname or IP (default: 34.179.141.137)
  --port INTEGER       MQTT broker port (default: 1883)
  --topic TEXT         MQTT topic (default: farm/field_01/sensors)
  --interval INTEGER   Publish interval in seconds (default: 60)
  --device-id TEXT     Device ID (default: field_sensor_01)
  --field-name TEXT    Field name (default: Field A - Tomatoes)
  --dry-run           Print data without publishing
  --verbose, -v       Enable verbose logging
  --help              Show this message and exit
```

### Environment Variables

```powershell
# Set environment variables (PowerShell)
$env:MQTT_BROKER = "192.168.1.100"
$env:MQTT_PORT = "1883"
$env:MQTT_TOPIC = "farm/field_02/sensors"
$env:PUBLISH_INTERVAL = "30"
$env:DEVICE_ID = "field_sensor_02"
$env:FIELD_NAME = "Field B - Corn"

# Run simulator (will use env vars)
python soil_sensor_simulator.py
```

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

## ☁️ Google Cloud Integration

### Prerequisites

1. Install Google Cloud SDK:
   ```powershell
   # Download from: https://cloud.google.com/sdk/docs/install
   # Or via Chocolatey:
   choco install gcloudsdk -y
   ```

2. Initialize gcloud:
   ```powershell
   gcloud init
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

### Option 1: Forward to Google Cloud Pub/Sub

#### Step 1: Create Pub/Sub Topic

```bash
# On your GCP VM (via SSH)
gcloud pubsub topics create soil-sensor-data
gcloud pubsub subscriptions create soil-sensor-sub --topic=soil-sensor-data
```

#### Step 2: Create Service Account

```bash
gcloud iam service-accounts create telegraf-pubsub \
    --display-name="Telegraf Pub/Sub Service Account"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:telegraf-pubsub@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/pubsub.publisher"

gcloud iam service-accounts keys create ~/telegraf-key.json \
    --iam-account=telegraf-pubsub@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

#### Step 3: Update Telegraf Config

Add to `telegraf/telegraf.conf`:

```toml
[[outputs.cloud_pubsub]]
  project = "YOUR_PROJECT_ID"
  topic = "soil-sensor-data"
  credentials_file = "/path/to/telegraf-key.json"
```

#### Step 4: Restart Telegraf

```powershell
cd docker
docker-compose restart telegraf
```

### Option 2: Forward to BigQuery

#### Step 1: Create BigQuery Dataset and Table

```bash
# Create dataset
bq mk --dataset YOUR_PROJECT_ID:soil_monitoring

# Create table
bq mk --table YOUR_PROJECT_ID:soil_monitoring.sensor_data \
  timestamp:TIMESTAMP,device_id:STRING,field_name:STRING,soil_moisture_percent:FLOAT,\
  soil_temperature_c:FLOAT,air_temperature_c:FLOAT,air_humidity_percent:FLOAT,\
  battery_voltage:FLOAT,lat:FLOAT,lon:FLOAT
```

#### Step 2: Use Cloud Function or Dataflow

Set up a Cloud Function to subscribe to Pub/Sub and insert into BigQuery, or use Dataflow for streaming pipeline.

---

## 🧪 Testing & Verification

### Test 1: Verify MQTT Messages

```powershell
# Subscribe to MQTT topic (if mosquitto_sub is installed locally)
mosquitto_sub -h localhost -t "farm/#" -v

# Or using Docker
docker exec -it mqtt_broker mosquitto_sub -h localhost -t "farm/#" -v
```

### Test 2: Query InfluxDB

```powershell
# Enter InfluxDB container
docker exec -it influxdb influx

# Run query
> from(bucket:"soil_data") |> range(start: -1h) |> limit(n:10)
```

### Test 3: Check Telegraf Logs

```powershell
docker logs telegraf -f
```

---

## 🛠️ Troubleshooting

### Issue: Simulator can't connect to broker

**Solution:**
- Verify broker IP: `Test-NetConnection -ComputerName 34.179.141.137 -Port 1883`
- Check GCP firewall rules allow port 1883
- Ensure Mosquitto is running on your VM

### Issue: No data in InfluxDB

**Solution:**
- Check Telegraf logs: `docker logs telegraf`
- Verify Telegraf config has correct InfluxDB token
- Ensure MQTT topic pattern matches: `farm/#`

### Issue: Grafana can't connect to InfluxDB

**Solution:**
- Use URL: `http://influxdb:8086` (not `localhost`)
- Verify token in Telegraf config matches InfluxDB admin token
- Check both containers are on same Docker network

### Issue: Docker containers won't start

**Solution:**
- Check Docker Desktop is running
- Verify ports aren't already in use: `netstat -an | findstr "1883 8086 3000"`
- Review container logs: `docker-compose logs`

---

## 📈 Next Steps / Enhancements

1. **Weather API Integration**
   - Pull weather forecast data from OpenWeatherMap or Google Weather
   - Store alongside sensor data for better irrigation decisions

2. **Automated Irrigation Control**
   - Add MQTT-controlled relay/valve simulator
   - Implement threshold-based automatic watering

3. **Machine Learning**
   - Train models on historical data to predict optimal watering times
   - Use Google Cloud AI Platform or Vertex AI

4. **Multi-Field Management**
   - Run multiple simulator instances with different device IDs
   - Create aggregated dashboards in Grafana

5. **Mobile Alerts**
   - Set up Grafana alerts for low soil moisture
   - Send notifications via email/SMS/Telegram

6. **Historical Analysis**
   - Create BigQuery views for weekly/monthly trends
   - Generate reports on water usage efficiency

---

## 📝 License

This is an educational IoT project for demonstration purposes.

---

## 🤝 Contributing

Feel free to fork and enhance this project! Suggestions:
- Add more sensor types (pH, NPK levels)
- Implement real hardware sensor integration
- Create mobile app frontend
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
