import psycopg2
import json
import paho.mqtt.client as mqtt
import random
import time
from datetime import datetime, timedelta, timezone
import threading

# PostgreSQL setup
conn = psycopg2.connect(dbname="smart_grid", user="mac", password="", host="localhost")
cursor = conn.cursor()

# Create table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS energy_readings (
        meter_id VARCHAR(20),
        timestamp TIMESTAMPTZ,
        power DOUBLE PRECISION,
        voltage DOUBLE PRECISION,
        current DOUBLE PRECISION,
        frequency DOUBLE PRECISION,
        energy DOUBLE PRECISION
    );
""")
conn.commit()

# --- MQTT Subscriber (stores data into DB) ---
def on_connect(client, userdata, flags, rc):
    print("MQTT Connected with result code", rc)
    client.subscribe("energy/meters/#")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        cursor.execute("""
            INSERT INTO energy_readings (meter_id, timestamp, power, voltage, current, frequency, energy)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            data['meter_id'], data['timestamp'], data['power'], data['voltage'],
            data['current'], data['frequency'], data['energy']
        ))
        conn.commit()
    except Exception as e:
        print("Insert error:", e)

# Define MQTT clients
subscriber_client = mqtt.Client()
publisher_client = mqtt.Client()

# Set MQTT username and password 
subscriber_client.username_pw_set("auca", "1234")
publisher_client.username_pw_set("auca", "1234")

subscriber_client.on_connect = on_connect
subscriber_client.on_message = on_message

subscriber_client.connect("localhost", 1883, 60)
publisher_client.connect("localhost", 1883, 60)

# --- MQTT Publisher (simulates smart meter data) ---
def simulate_and_publish():
    meter_ids = [str(1000000000 + i) for i in range(500)]
    start_time = datetime.now(timezone.utc)

    for interval in range(12):  # simulate 1 hour (12 x 5min)
        current_time = start_time + timedelta(minutes=interval * 5)
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
                "energy": round(base_power * 5 / 60, 2)
            }

            topic = f"energy/meters/{meter_id}"
            publisher_client.publish(topic, json.dumps(data))

        print(f"[{interval + 1}/12] Published at {current_time}")
        time.sleep(1)

# Run publisher in a background thread
publisher_thread = threading.Thread(target=simulate_and_publish)
publisher_thread.start()

# Start subscriber loop (main thread)
subscriber_client.loop_forever()
