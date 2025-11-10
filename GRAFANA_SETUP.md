# Grafana Dashboard Setup Guide

## Step 1: Access Grafana

1. Open your browser and navigate to: `http://localhost:3000`
2. Login with default credentials:
   - **Username**: `admin`
   - **Password**: `admin`
3. You'll be prompted to change the password (you can skip this for local development)

## Step 2: Add InfluxDB Data Source

1. Click the **☰ menu** (hamburger menu) in the top-left
2. Go to **Connections → Data sources**
3. Click **Add data source**
4. Select **InfluxDB**
5. Configure with these settings:

   **Query Language:** `Flux`
   
   **HTTP:**
   - **URL**: `http://influxdb:8086`
   
   **InfluxDB Details:**
   - **Organization**: `smartfarm`
   - **Token**: `your-super-secret-auth-token`
   - **Default Bucket**: `soil_data`

6. Click **Save & Test** - you should see "datasource is working"

## Step 3: Create Your First Dashboard

1. Click **☰ menu → Dashboards**
2. Click **New → New Dashboard**
3. Click **+ Add visualization**
4. Select your InfluxDB data source

## Step 4: Add Panels

### Panel 1: Soil Moisture (Gauge)

**Query (Flux):**
```flux
from(bucket: "soil_data")
  |> range(start: -5m)
  |> filter(fn: (r) => r._measurement == "mqtt_consumer")
  |> filter(fn: (r) => r._field == "soil_moisture_percent")
  |> last()
```

**Visualization Settings:**
- **Panel type**: Gauge
- **Title**: "Soil Moisture %"
- **Unit**: Percent (0-100)
- **Thresholds**:
  - Red: 0-30 (Too dry)
  - Yellow: 30-40 (Low)
  - Green: 40-60 (Optimal)
  - Yellow: 60-70 (High)
  - Red: 70-100 (Too wet)

### Panel 2: Soil Moisture Over Time (Time Series)

**Query (Flux):**
```flux
from(bucket: "soil_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "mqtt_consumer")
  |> filter(fn: (r) => r._field == "soil_moisture_percent")
  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
```

**Visualization Settings:**
- **Panel type**: Time series
- **Title**: "Soil Moisture Trend"
- **Unit**: Percent (0-100)
- **Legend**: Bottom
- **Fill opacity**: 20

### Panel 3: Temperature Comparison (Time Series)

**Query (Flux):**
```flux
from(bucket: "soil_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "mqtt_consumer")
  |> filter(fn: (r) => r._field == "soil_temperature_c" or r._field == "air_temperature_c")
  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
```

**Visualization Settings:**
- **Panel type**: Time series
- **Title**: "Temperature (Soil vs Air)"
- **Unit**: Celsius (°C)
- **Legend**: Show with field names

### Panel 4: Air Humidity (Gauge)

**Query (Flux):**
```flux
from(bucket: "soil_data")
  |> range(start: -5m)
  |> filter(fn: (r) => r._measurement == "mqtt_consumer")
  |> filter(fn: (r) => r._field == "air_humidity_percent")
  |> last()
```

**Visualization Settings:**
- **Panel type**: Gauge
- **Title**: "Air Humidity %"
- **Unit**: Percent (0-100)
- **Thresholds**:
  - Red: 0-30 (Too dry)
  - Yellow: 30-40 (Low)
  - Green: 40-70 (Optimal)
  - Yellow: 70-80 (High)
  - Red: 80-100 (Too humid)

### Panel 5: Battery Voltage (Stat)

**Query (Flux):**
```flux
from(bucket: "soil_data")
  |> range(start: -5m)
  |> filter(fn: (r) => r._measurement == "mqtt_consumer")
  |> filter(fn: (r) => r._field == "battery_voltage")
  |> last()
```

**Visualization Settings:**
- **Panel type**: Stat
- **Title**: "Battery Voltage"
- **Unit**: Volt (V)
- **Thresholds**:
  - Red: 0-3.5 (Low battery)
  - Yellow: 3.5-3.8 (Medium)
  - Green: 3.8-4.2 (Good)

### Panel 6: Multi-Stat Summary

**Query (Flux):**
```flux
from(bucket: "soil_data")
  |> range(start: -5m)
  |> filter(fn: (r) => r._measurement == "mqtt_consumer")
  |> filter(fn: (r) => r._field == "soil_moisture_percent" 
            or r._field == "soil_temperature_c" 
            or r._field == "air_temperature_c" 
            or r._field == "air_humidity_percent")
  |> last()
  |> keep(columns: ["_field", "_value"])
```

**Visualization Settings:**
- **Panel type**: Stat
- **Title**: "Current Readings"
- **Orientation**: Horizontal
- **Color mode**: Value
- **Graph mode**: None

## Step 5: Save Your Dashboard

1. Click the **💾 Save dashboard** icon in the top-right
2. Give it a name: "Smart Agriculture - Field Monitoring"
3. Add a description: "Real-time soil and environmental monitoring for Field A"
4. Click **Save**

## Step 6: Set Dashboard Refresh Rate

1. In the top-right corner, click the **⟳ refresh** dropdown
2. Set auto-refresh to **30s** or **1m**
3. This will keep your dashboard updated with the latest sensor readings

## Suggested Dashboard Layout

```
┌─────────────────────────────────────────────────────────────┐
│ Smart Agriculture - Field Monitoring                        │
├─────────────────┬──────────────────┬────────────────────────┤
│                 │                  │                        │
│  Soil Moisture  │  Air Humidity   │   Battery Voltage      │
│     (Gauge)     │     (Gauge)     │       (Stat)           │
│                 │                  │                        │
├─────────────────┴──────────────────┴────────────────────────┤
│                                                              │
│         Soil Moisture Trend (Time Series - 1 hour)          │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│      Temperature Comparison (Time Series - 1 hour)          │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                    Current Readings (Multi-Stat)            │
└──────────────────────────────────────────────────────────────┘
```

## Tips

- Use **Variables** to create a dropdown for selecting different fields or devices
- Set up **Alerts** to notify when soil moisture drops below threshold
- Create **Annotations** to mark irrigation events
- Export your dashboard as JSON to share with others

## Troubleshooting

### No data showing in panels?

1. Check the time range (top-right corner) - set to "Last 1 hour"
2. Verify your Flux query returns data in the Query inspector (click query tab)
3. Ensure the simulator is running: check terminal for "Published message" logs
4. Verify InfluxDB has data: Run the query from Step 2 in InfluxDB UI

### Data source connection failed?

- Use `http://influxdb:8086` not `http://localhost:8086`
- Verify the token matches the one in `docker-compose.yml`
- Check that InfluxDB container is running: `docker-compose ps`

---

**Enjoy monitoring your smart farm! 🌱📊**
