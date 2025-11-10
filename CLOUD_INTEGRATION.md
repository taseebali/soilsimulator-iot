# Next Steps: Google Cloud Integration Guide

## ✅ What's Working Now (Local Stack)

Your Smart Agriculture IoT solution is fully operational locally:

- ✅ **Sensor Simulator**: Publishing data every 2 minutes (120 seconds)
- ✅ **MQTT Broker (Mosquitto)**: Receiving sensor messages
- ✅ **Telegraf**: Collecting MQTT data
- ✅ **InfluxDB**: Storing time-series sensor data
- ✅ **Grafana**: Available at `http://localhost:3000` for visualization

**Data Pipeline Flow:**
```
Sensor Simulator → MQTT (port 1883) → Telegraf → InfluxDB → Grafana
```

---

## 🚀 Google Cloud Integration Options

Now that your local stack is working, you can extend it to Google Cloud Platform for:
- **Advanced analytics** (BigQuery)
- **Real-time streaming** (Pub/Sub)
- **Machine learning** (Vertex AI)
- **Weather data integration** (Weather API + Cloud Functions)
- **Scalability** (handle multiple farms/fields)

---

## Option 1: Forward Data to Google Cloud Pub/Sub

### Benefits
- Decouple data producers from consumers
- Enable multiple subscribers (BigQuery, Cloud Functions, etc.)
- Built-in retry and delivery guarantees
- Foundation for real-time processing

### Setup Steps

#### 1. Create Pub/Sub Topic and Subscription

```bash
# On your GCP VM or local machine with gcloud CLI
gcloud pubsub topics create soil-sensor-data

gcloud pubsub subscriptions create soil-sensor-sub \
    --topic=soil-sensor-data
```

#### 2. Create Service Account for Telegraf

```bash
# Create service account
gcloud iam service-accounts create telegraf-pubsub \
    --display-name="Telegraf Pub/Sub Publisher"

# Grant Pub/Sub publisher role
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:telegraf-pubsub@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/pubsub.publisher"

# Create and download key
gcloud iam service-accounts keys create telegraf-key.json \
    --iam-account=telegraf-pubsub@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

#### 3. Update Telegraf Configuration

Add to `telegraf/telegraf.conf`:

```toml
[[outputs.cloud_pubsub]]
  ## GCP Project
  project = "YOUR_PROJECT_ID"
  
  ## Pub/Sub topic
  topic = "soil-sensor-data"
  
  ## Service account credentials
  credentials_file = "/etc/telegraf/telegraf-key.json"
  
  ## Data format
  data_format = "json"
```

#### 4. Mount Service Account Key in Docker

Update `docker/docker-compose.yml`:

```yaml
telegraf:
  image: telegraf:1.28
  container_name: telegraf
  volumes:
    - ../telegraf/telegraf.conf:/etc/telegraf/telegraf.conf:ro
    - ../telegraf/telegraf-key.json:/etc/telegraf/telegraf-key.json:ro
  depends_on:
    - mosquitto
    - influxdb
  restart: unless-stopped
```

#### 5. Restart Telegraf

```powershell
cd docker
docker-compose restart telegraf
docker logs telegraf -f
```

#### 6. Verify Messages in Pub/Sub

```bash
# Pull messages from subscription
gcloud pubsub subscriptions pull soil-sensor-sub --limit=5
```

---

## Option 2: Stream Data to BigQuery

### Benefits
- SQL queries on historical sensor data
- Join with weather data
- Generate reports and insights
- ML training datasets

### Setup Steps

#### 1. Create BigQuery Dataset and Table

```bash
# Create dataset
bq mk --dataset YOUR_PROJECT_ID:soil_monitoring

# Create table with schema
bq mk --table YOUR_PROJECT_ID:soil_monitoring.sensor_data \
  timestamp:TIMESTAMP,\
  device_id:STRING,\
  field_name:STRING,\
  soil_moisture_percent:FLOAT64,\
  soil_temperature_c:FLOAT64,\
  air_temperature_c:FLOAT64,\
  air_humidity_percent:FLOAT64,\
  battery_voltage:FLOAT64,\
  lat:FLOAT64,\
  lon:FLOAT64
```

#### 2. Create Cloud Function to Insert from Pub/Sub

**Trigger**: Pub/Sub topic `soil-sensor-data`

**Code** (`main.py`):
```python
import base64
import json
from google.cloud import bigquery

def process_sensor_data(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic."""
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    data = json.loads(pubsub_message)
    
    # Prepare BigQuery row
    row = {
        'timestamp': data['timestamp'],
        'device_id': data['device_id'],
        'field_name': data['field_name'],
        'soil_moisture_percent': data['soil_moisture_percent'],
        'soil_temperature_c': data['soil_temperature_c'],
        'air_temperature_c': data['air_temperature_c'],
        'air_humidity_percent': data['air_humidity_percent'],
        'battery_voltage': data['battery_voltage'],
        'lat': data['location']['lat'],
        'lon': data['location']['lon']
    }
    
    # Insert into BigQuery
    client = bigquery.Client()
    table_id = "YOUR_PROJECT_ID.soil_monitoring.sensor_data"
    
    errors = client.insert_rows_json(table_id, [row])
    if errors:
        print(f"Errors: {errors}")
        raise Exception("Failed to insert row")
    
    print(f"Inserted row for device {data['device_id']}")
```

**Deploy**:
```bash
gcloud functions deploy process_sensor_data \
    --runtime python39 \
    --trigger-topic soil-sensor-data \
    --entry-point process_sensor_data
```

#### 3. Query Your Data

```sql
-- Get latest readings
SELECT *
FROM `YOUR_PROJECT_ID.soil_monitoring.sensor_data`
ORDER BY timestamp DESC
LIMIT 10;

-- Average moisture per hour
SELECT
  TIMESTAMP_TRUNC(timestamp, HOUR) as hour,
  device_id,
  AVG(soil_moisture_percent) as avg_moisture
FROM `YOUR_PROJECT_ID.soil_monitoring.sensor_data`
WHERE timestamp > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
GROUP BY hour, device_id
ORDER BY hour DESC;
```

---

## Option 3: Add Weather Data Integration

### Benefits
- Correlate soil conditions with weather
- Predict irrigation needs
- Optimize watering schedules

### Setup Steps

#### 1. Get OpenWeatherMap API Key

Sign up at: https://openweathermap.org/api

#### 2. Create Cloud Function for Weather Data

**Trigger**: Cloud Scheduler (runs every 15 minutes)

**Code** (`weather_collector.py`):
```python
import requests
from google.cloud import bigquery
from datetime import datetime

def collect_weather_data(event, context):
    """Collects weather data and stores in BigQuery."""
    
    API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"
    LAT = 52.52  # Your field location
    LON = 13.405
    
    # Fetch current weather
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    weather = response.json()
    
    # Prepare BigQuery row
    row = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'location_lat': LAT,
        'location_lon': LON,
        'temperature': weather['main']['temp'],
        'humidity': weather['main']['humidity'],
        'pressure': weather['main']['pressure'],
        'weather_condition': weather['weather'][0]['main'],
        'weather_description': weather['weather'][0]['description'],
        'wind_speed': weather['wind']['speed'],
        'clouds': weather['clouds']['all'],
        'rain_1h': weather.get('rain', {}).get('1h', 0)
    }
    
    # Insert into BigQuery
    client = bigquery.Client()
    table_id = "YOUR_PROJECT_ID.soil_monitoring.weather_data"
    
    errors = client.insert_rows_json(table_id, [row])
    if errors:
        print(f"Errors: {errors}")
    else:
        print(f"Weather data inserted")
```

#### 3. Create BigQuery Table for Weather

```bash
bq mk --table YOUR_PROJECT_ID:soil_monitoring.weather_data \
  timestamp:TIMESTAMP,\
  location_lat:FLOAT64,\
  location_lon:FLOAT64,\
  temperature:FLOAT64,\
  humidity:FLOAT64,\
  pressure:FLOAT64,\
  weather_condition:STRING,\
  weather_description:STRING,\
  wind_speed:FLOAT64,\
  clouds:FLOAT64,\
  rain_1h:FLOAT64
```

#### 4. Join Sensor and Weather Data

```sql
SELECT
  s.timestamp,
  s.device_id,
  s.soil_moisture_percent,
  s.soil_temperature_c,
  w.temperature as weather_temp,
  w.humidity as weather_humidity,
  w.rain_1h,
  w.weather_description
FROM `YOUR_PROJECT_ID.soil_monitoring.sensor_data` s
LEFT JOIN `YOUR_PROJECT_ID.soil_monitoring.weather_data` w
  ON TIMESTAMP_DIFF(s.timestamp, w.timestamp, MINUTE) BETWEEN -15 AND 15
WHERE s.timestamp > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
ORDER BY s.timestamp DESC;
```

---

## Option 4: Machine Learning for Irrigation Prediction

### Benefits
- Predict when irrigation is needed
- Optimize water usage
- Reduce costs and waste

### Setup Steps

#### 1. Create ML Dataset in BigQuery

```sql
-- Create training dataset
CREATE OR REPLACE TABLE `YOUR_PROJECT_ID.soil_monitoring.ml_training_data` AS
SELECT
  s.timestamp,
  s.soil_moisture_percent,
  s.soil_temperature_c,
  s.air_temperature_c,
  s.air_humidity_percent,
  w.temperature as weather_temp,
  w.humidity as weather_humidity,
  w.rain_1h,
  -- Label: 1 if irrigation happened in next 2 hours, 0 otherwise
  CASE 
    WHEN LEAD(s.soil_moisture_percent, 1) OVER (ORDER BY s.timestamp) > s.soil_moisture_percent + 10 
    THEN 1 
    ELSE 0 
  END as needs_irrigation
FROM `YOUR_PROJECT_ID.soil_monitoring.sensor_data` s
LEFT JOIN `YOUR_PROJECT_ID.soil_monitoring.weather_data` w
  ON TIMESTAMP_DIFF(s.timestamp, w.timestamp, MINUTE) BETWEEN -15 AND 15
WHERE s.timestamp > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY);
```

#### 2. Train Model with BigQuery ML

```sql
CREATE OR REPLACE MODEL `YOUR_PROJECT_ID.soil_monitoring.irrigation_predictor`
OPTIONS(
  model_type='LOGISTIC_REG',
  input_label_cols=['needs_irrigation']
) AS
SELECT
  soil_moisture_percent,
  soil_temperature_c,
  air_temperature_c,
  air_humidity_percent,
  weather_temp,
  weather_humidity,
  rain_1h,
  needs_irrigation
FROM `YOUR_PROJECT_ID.soil_monitoring.ml_training_data`;
```

#### 3. Make Predictions

```sql
-- Predict if irrigation is needed for current conditions
SELECT
  *,
  predicted_needs_irrigation,
  predicted_needs_irrigation_probs[OFFSET(1)].prob as irrigation_probability
FROM ML.PREDICT(
  MODEL `YOUR_PROJECT_ID.soil_monitoring.irrigation_predictor`,
  (
    SELECT
      soil_moisture_percent,
      soil_temperature_c,
      air_temperature_c,
      air_humidity_percent,
      weather_temp,
      weather_humidity,
      rain_1h
    FROM `YOUR_PROJECT_ID.soil_monitoring.sensor_data` s
    LEFT JOIN `YOUR_PROJECT_ID.soil_monitoring.weather_data` w
      ON TIMESTAMP_DIFF(s.timestamp, w.timestamp, MINUTE) BETWEEN -15 AND 15
    ORDER BY s.timestamp DESC
    LIMIT 1
  )
);
```

---

## 📋 Recommended Implementation Order

1. **Week 1**: Get Pub/Sub working (Option 1)
   - Easiest integration
   - Foundation for everything else
   - Low cost

2. **Week 2**: Add BigQuery streaming (Option 2)
   - Start collecting historical data
   - Run basic analytics queries
   - Create reports

3. **Week 3**: Integrate weather data (Option 3)
   - Enrich your analysis
   - More valuable insights
   - Better predictions

4. **Week 4**: Train ML models (Option 4)
   - Need historical data first
   - Requires both sensor and weather data
   - Most advanced feature

---

## 💰 Cost Estimates (Monthly)

- **Pub/Sub**: $0.40 per million messages (~$0.02/month for single field)
- **BigQuery**: $5/TB storage + $5/TB queries (~$1/month for single field)
- **Cloud Functions**: $0.40 per million invocations (~$0.10/month)
- **VM (if keeping GCP VM)**: ~$5-10/month for small instance

**Total**: ~$6-12/month for full cloud integration

---

## 🔧 Quick Commands Reference

```powershell
# Check local services
docker-compose ps
docker logs telegraf -f
docker logs mosquitto -f

# Test simulator with GCP broker
python soil_sensor_simulator.py --broker 34.179.141.137

# Test with local broker
python soil_sensor_simulator.py --broker localhost

# Query InfluxDB
docker exec influxdb influx query 'from(bucket:"soil_data") |> range(start: -1h) |> limit(n:10)' --org smartfarm --token your-super-secret-auth-token

# Subscribe to MQTT locally
docker exec mqtt_broker mosquitto_sub -h localhost -t "farm/#" -v
```

---

## 📞 Need Help?

1. Check container logs: `docker logs <container_name>`
2. Verify network connectivity: `Test-NetConnection -ComputerName <host> -Port <port>`
3. Review GCP logs: `gcloud logging read`
4. Check BigQuery jobs: `bq ls -j`

---

**You're ready for cloud integration! Start with Pub/Sub and scale from there. 🚀☁️**
