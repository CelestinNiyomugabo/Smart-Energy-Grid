# 📊 Smart Energy Grid Monitoring System

This project implements a simulated smart energy grid monitoring system using EMQX, TimescaleDB, and Streamlit. It includes real-time data generation, ingestion, storage, compression, aggregation, and interactive visualization.

---

## 📁 Repository Structure

```bash
├── dashboard.py              # Streamlit dashboard
├── subscriber_publisher.py  # MQTT data generator and subscriber (5 min, 500 meters)
├── historic_data_gen.py     # Generates 2-week batch data (for 4.2M+ rows)
├── requirements.txt         # Required Python packages
├── README.md                # Project overview and instructions
└── latex_report.tex         # LaTeX source report
```

---

## 🚀 Setup Instructions

### 1. Install Requirements
```bash
pip install -r requirements.txt
```

### 2. Start Services
- EMQX: `emqx start`
- PostgreSQL / TimescaleDB: ensure `smart_grid` DB is created

### 3. Launch Dashboard
```bash
streamlit run dashboard.py
```

---

## 📥 Data Generation & Loading

### Real-Time Streaming:
```python
# In subscriber_publisher.py
publisher_client.publish(topic, json.dumps(data))
```

### Historical Data:
```bash
# historic_data_gen.py simulates 14 days for 500 meters every 5 minutes
count = 500 * 12 * 24 * 14 = 2,016,000 rows
```

---

## 🔧 TimescaleDB Configuration

### Convert to Hypertable
```sql
CREATE EXTENSION IF NOT EXISTS timescaledb;
SELECT create_hypertable('energy_readings', 'timestamp', migrate_data => true, chunk_time_interval => INTERVAL '1 day');
```

### Clone & Chunk Variants
```sql
CREATE TABLE energy_readings_3h (LIKE energy_readings INCLUDING ALL);
CREATE TABLE energy_readings_week (LIKE energy_readings INCLUDING ALL);
SELECT create_hypertable('energy_readings_3h', 'timestamp', chunk_time_interval => INTERVAL '3 hours');
SELECT create_hypertable('energy_readings_week', 'timestamp', chunk_time_interval => INTERVAL '1 week');
INSERT INTO energy_readings_3h SELECT * FROM energy_readings;
INSERT INTO energy_readings_week SELECT * FROM energy_readings;
```

---

## 🧪 Queries Executed

### Query 1: Hourly Power Today
```sql
SELECT time_bucket('1 hour', timestamp) AS hour, AVG(power) as avg_power
FROM energy_readings
WHERE timestamp >= DATE_TRUNC('day', NOW())
GROUP BY hour ORDER BY hour;
```

### Query 2: Peak 15-Minute Intervals This Week
```sql
SELECT time_bucket('15 minutes', timestamp) AS period, AVG(power) as avg_power
FROM energy_readings
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY period ORDER BY avg_power DESC LIMIT 10;
```

### Query 3: Monthly Consumption by Meter
```sql
SELECT meter_id, DATE_TRUNC('month', timestamp) AS month, SUM(energy) AS total_energy
FROM energy_readings
GROUP BY meter_id, month
ORDER BY month, total_energy DESC;
```

### Query 4: Full Dataset Scan
```sql
SELECT COUNT(*), AVG(power), MAX(power), MIN(power) FROM energy_readings;
```

---

## 🗜 Compression

### Execute Compression
```sql
SELECT compress_chunk(format('%I.%I', chunk_schema, chunk_name)::regclass)
FROM timescaledb_information.chunks
WHERE hypertable_name IN ('energy_readings', 'energy_readings_3h', 'energy_readings_week')
AND is_compressed = false;
```

### View Table Sizes
```sql
SELECT hypertable_name, pg_size_pretty(total_bytes) AS size
FROM hypertable_compression_stats;
```

---

## ⏳ Continuous Aggregation
```sql
CREATE MATERIALIZED VIEW energy_readings_15min
WITH (timescaledb.continuous) AS
SELECT
    meter_id,
    time_bucket('15 minutes', timestamp) AS bucket,
    AVG(power) AS avg_power,
    MAX(power) AS max_power,
    SUM(energy) AS total_energy
FROM energy_readings
GROUP BY meter_id, bucket;
```

---

## 📊 Dashboard Features (Streamlit)
- Live Readings (last 1 hour)
- Daily Energy Totals
- Meter-Level Trends
- Aggregated Insights

---
