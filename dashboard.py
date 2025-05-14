import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
from datetime import datetime

# --- DATABASE CONFIG ---
DB_CONFIG = {
    'dbname': 'smart_grid',
    'user': 'mac',
    'password': '',  # Update if needed
    'host': 'localhost'
}

# --- PAGE CONFIG ---
st.set_page_config(page_title="Smart Energy Dashboard", layout="wide")
st.title("⚡ Smart Energy Grid Dashboard")

# --- DB CONNECTION ---
@st.cache_data
def run_query(query):
    with psycopg2.connect(**DB_CONFIG) as conn:
        return pd.read_sql_query(query, conn)

# --- SECTIONS ---
st.header("Live readings (last hour)")
live_df = run_query('''
    SELECT * FROM energy_readings
    WHERE timestamp >= NOW() - INTERVAL '1 hour'
    ORDER BY timestamp DESC
    LIMIT 100;
''')
st.dataframe(live_df, use_container_width=True)

# --- DAILY ENERGY TRENDS ---
st.header("📊 Daily Energy Consumption")
daily_df = run_query('''
    SELECT date_trunc('day', timestamp) AS day, SUM(energy) AS total_energy
    FROM energy_readings
    GROUP BY day
    ORDER BY day;
''')
fig_daily = px.bar(daily_df, x='day', y='total_energy', title='Daily Energy Usage')
st.plotly_chart(fig_daily, use_container_width=True)

# --- TOP METERS ---
st.header("Top 10 meters this Month")
top_df = run_query('''
    SELECT meter_id, SUM(energy) AS total_energy
    FROM energy_readings
    WHERE timestamp >= NOW() - INTERVAL '1 month'
    GROUP BY meter_id
    ORDER BY total_energy DESC
    LIMIT 10;
''')
fig_top = px.bar(top_df, x='meter_id', y='total_energy', title='Top Energy Consumers')
st.plotly_chart(fig_top, use_container_width=True)

# --- PERFORMANCE COMPARISON ---
st.header("⏱ Query Performance Comparison")
perf_data = pd.DataFrame({
    'Query': ['Raw Query', 'Continuous Aggregate'],
    'Execution Time (ms)': [31.76, 2.63]
})
fig_perf = px.bar(perf_data, x='Query', y='Execution Time (ms)', title='Query Performance')
st.plotly_chart(fig_perf, use_container_width=True)

# --- FOOTER ---
st.caption("Developed by Celestin, Frank, and Claude")
st.markdown("""
    <div class="css-qri22k">
        © 2025 Smart Energy Grid Project - Big Data Analytics (AUCA).
    </div>
""", unsafe_allow_html=True)
