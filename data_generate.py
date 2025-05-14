import paho.mqtt.client as mqtt
import json
import random
import time
from datetime import datetime, timedelta, timezone

# --- Configuration ---
USERNAME = "auca"  
PASSWORD = "1234"  
BROKER = "localhost"
PORT = 1883
METER_COUNT = 500
DAYS = 14
INTERVAL_MINUTES = 5
THROTTLE_DELAY = 0.3  

# --- MQTT Setup ---
client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)
client.connect(BROKER, PORT, 60)

# --- Generate Meter IDs ---
meter_ids = [str(1000000000 + i) for i in range(METER_COUNT)]

# --- Simulate 2 Weeks of Data ---
start_time = datetime.now(timezone.utc) - timedelta(days=DAYS)
total_intervals = (24 * 60 // INTERVAL_MINUTES) * DAYS  # 288 intervals/day

for interval in range(total_intervals):
    current_time = start_time + timedelta(minutes=interval * INTERVAL_MINUTES)
    for meter_id in meter_ids:
        hour = current_time.hour
        base_power = random.uniform(200, 500) if 6 <= hour <= 9 or 18 <= hour <= 22 else random.uniform(50, 150)

        data = {
            "meter_id": meter_id,
            "timestamp": current_time.isoformat(),
            "power": round(base_power, 2),
            "voltage": round(random.uniform(210, 250), 2),
            "current": round(random.uniform(0.5, 2.5), 2),
            "frequency": round(random.uniform(49.5, 50.5), 2),
            "energy": round(base_power * INTERVAL_MINUTES / 60, 2)
        }

        topic = f"energy/meters/{meter_id}"
        client.publish(topic, json.dumps(data))

    print(f"[{interval + 1}/{total_intervals}] Published batch at {current_time}")
    time.sleep(THROTTLE_DELAY)

client.disconnect()
