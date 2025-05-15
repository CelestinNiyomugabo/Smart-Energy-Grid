import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="Smart Energy Grid Dashboard", layout="wide", initial_sidebar_state="expanded")

# --- DATABASE CONFIG ---
DB_CONFIG = {
    'dbname': 'smart_grid',
    'user': 'mac',
    'password': '',  # Update as necessary
    'host': 'localhost'
}

# --- DB CONNECTION ---
@st.cache_data
def run_query(query):
    with psycopg2.connect(**DB_CONFIG) as conn:
        return pd.read_sql_query(query, conn)

# --- DASHBOARD HEADER ---
st.title(" Smart Energy Grid Dashboard - Group 2")
st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .metric-container {
        background-color: #1e1e1e;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(255, 255, 255, 0.05);
    }
    </style>
""", unsafe_allow_html=True)

# --- SUMMARY STATS ---
st.markdown("### Overview")
sum_df = run_query("""
    SELECT 
        COUNT(*) as total_records, 
        COUNT(DISTINCT meter_id) as meter_count, 
        COUNT(*)::float/COUNT(DISTINCT meter_id) as avg_per_meter, 
        COUNT(*)::float/14 as avg_per_day 
    FROM energy_readings;
""")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Meters", int(sum_df['meter_count'][0]))
col2.metric("Total Records", int(sum_df['total_records'][0]))
col3.metric("Avg Records per Meter", f"{sum_df['avg_per_meter'][0]:,.2f}")
col4.metric("Avg Records per Day", f"{sum_df['avg_per_day'][0]:,.0f}")

# --- LIVE READINGS ---
st.header(" Real-Time Meter Readings (Last Hour)")
live_df = run_query('''
    SELECT * FROM energy_readings
    WHERE timestamp >= NOW() - INTERVAL '1 hour'
    ORDER BY timestamp DESC
    LIMIT 100;
''')
st.dataframe(live_df, use_container_width=True)

# --- DAILY CONSUMPTION: TODAY VS YESTERDAY ---
st.header(" Daily Consumption Patterns: Today vs Yesterday")
daily_df = run_query('''
    SELECT
        DATE_TRUNC('day', timestamp) AS day,
        SUM(energy) AS total_energy
    FROM energy_readings
    WHERE timestamp >= NOW() - INTERVAL '2 days'
    GROUP BY day
    ORDER BY day;
''')
fig_daily = px.bar(daily_df, x='day', y='total_energy', title='Energy Consumption: Today vs Yesterday')
st.plotly_chart(fig_daily, use_container_width=True)

# --- WEEKLY TRENDS ---
st.header(" Weekly Trends in Energy Usage")
weekly_df = run_query('''
    SELECT DATE_TRUNC('day', timestamp) AS day, AVG(power) AS avg_power
    FROM energy_readings
    WHERE timestamp >= NOW() - INTERVAL '7 days'
    GROUP BY day
    ORDER BY day;
''')
fig_weekly = px.line(weekly_df, x='day', y='avg_power', title='Weekly Average Power Usage')
st.plotly_chart(fig_weekly, use_container_width=True)

# --- MONTHLY ENERGY USAGE BY REGION ---
st.header(" Monthly Energy Usage by Region")
region_df = run_query('''
    SELECT LEFT(meter_id, 1) AS region, DATE_TRUNC('month', timestamp) AS month, SUM(energy) AS total_energy
    FROM energy_readings
    GROUP BY region, month
    ORDER BY month, region;
''')
fig_region = px.bar(region_df, x='region', y='total_energy', color='month', barmode='group', title='Energy Usage by Region')
st.plotly_chart(fig_region, use_container_width=True)

# --- PERFORMANCE METRICS PANEL ---
st.header(" Performance Metrics")

# Query execution time comparison
st.subheader("Query Execution Time")
perf_data = pd.DataFrame({
    'Query': ['Raw Query', 'Continuous Aggregate'],
    'Execution Time (ms)': [31.756, 2.625]
})
fig_perf = px.bar(perf_data, x='Query', y='Execution Time (ms)', title='Query Time: Raw vs Aggregated')
st.plotly_chart(fig_perf, use_container_width=True)

# Storage efficiency gains from compression
st.subheader("Storage Efficiency")
storage_df = pd.DataFrame({
    'Table': ['energy_readings', 'energy_readings_3h', 'energy_readings_week'],
    'Before Compression (MB)': [211, 215, 211],
    'After Compression (MB)': [89, 96, 88]
})
st.dataframe(storage_df)

# Chunk strategy comparisons
st.subheader("Chunk Strategy Performance (Query 3)")
chunk_perf = pd.DataFrame({
    'Chunk Interval': ['3 Hours', '1 Day', '1 Week'],
    'Execution Time (ms)': [186.553, 166.829, 173.673]
})
fig_chunk = px.bar(chunk_perf, x='Chunk Interval', y='Execution Time (ms)', title='Query Performance by Chunk Interval')
st.plotly_chart(fig_chunk, use_container_width=True)

# --- FOOTER ---
st.markdown("---")
st.caption("Developed by Celestin, Frank, and Claude | AUCA - Big Data Analytics")
