# Step 1: Install the required tools and packages
# Step 2: Start EMQX (emqxstart). We have verified the EMQX status from: http://localhost:18083/status
# Step 3: Create a timescale DB: CREATE DATABASE smart_grid;
# Step 4: Login to newly created DB: \c smart_grid


import psycopg2
import json
import paho.mqtt.client as mqtt

# PostgreSQL setup
conn = psycopg2.connect(dbname="smart_grid", user="mac", password="", host="localhost")
cursor = conn.cursor()

# Create the table
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

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected:", rc)
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
        print("Error:", e)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)
client.loop_forever()


