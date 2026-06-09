import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import random
import streamlit as st
import time
from sqlalchemy import create_engine, text


load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

connection_string = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(connection_string)


with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS sensor_history (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            segment_id TEXT,
            pressure INT,
            temperature REAL,
            water_dist REAL,
            risk_status TEXT
        );
    """))

#1 =====================================================================

@st.cache_data
def load_spatial_data_from_postgis():

    query = """
    SELECT 
        s.segment_id,
        (SELECT MIN(ST_Distance(s.geometry, l.geometry)) FROM lakes l) AS lake_dist_m,
        (SELECT MIN(ST_Distance(s.geometry, r.geometry)) FROM rivers r) AS river_dist_m
    FROM pipeline_segments s;
    """
    df = pd.read_sql(query, engine)
    
    df['water_distance'] = df[['lake_dist_m', 'river_dist_m']].min(axis=1)
    return df


db_segments = load_spatial_data_from_postgis()

# 2 =====================================================================

class PipelineSegment:
    def __init__(self, segment_id, water_dist):
        self.water_dist = float(round(water_dist, 1))
        
        self.is_underwater_crossing = self.water_dist <= 5.0
        
        suffix = " [River Crossing]" if self.is_underwater_crossing else ""
        self.segment_id = f"Segment {int(segment_id)}{suffix}"
        
        self.pressure = 0
        self.temperature = 0

    def read_sensor(self):
        self.pressure = random.randint(700, 1200)
        self.temperature = random.uniform(10, 45)

    def get_risk_level(self):
        
        if self.is_underwater_crossing:
            if self.pressure > 1150: 
                return '🚨 CRITICAL: Underwater crossing failure!'
            if self.pressure > 1080:
                return '⚠️ High Pressure in River Bed'
            return 'Normal (Underwater Mode)'
        
        
        if self.pressure > 1100 and self.temperature > 38:
            return '🚨 CRITICAL: Thermal explosion!'
        if self.pressure > 1050 and self.water_dist < 150:
            return '🚨 CRITICAL: Risk of water leakage!'
        if self.pressure > 1100:
            return '⚠️ High Pressure'
        if self.temperature > 40:
            return '🔥 High Temperature'
        return 'Normal'

digital_twin_segments = []
for _, row in db_segments.iterrows():
    obj = PipelineSegment(segment_id=row['segment_id'], water_dist=row['water_distance'])
    digital_twin_segments.append(obj)

#3 =====================================================================
st.set_page_config(layout="wide") 
st.title("🛰️ Enterprise Digital Twin of the Oil Pipeline (PostGIS + DBMS)")

st.sidebar.header("🎛️ Control Panel")
run_system = st.sidebar.checkbox("Enable Pipeline Monitoring", value=True)


if st.sidebar.button("🗑️ Clear Logs History in DB"):
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE sensor_history;"))
    st.sidebar.success("History cleared!")


metrics_placeholder = st.empty()
table_title_placeholder = st.empty()
table_placeholder = st.empty()
chart_title_placeholder = st.empty()
chart_placeholder = st.empty()

if run_system:
    current_data_to_show = []
    db_logs = []
    total_pressure = 0
    critical_count = 0

    num_segments = len(digital_twin_segments)

    
    for seg in digital_twin_segments:
        seg.read_sensor()
        status = seg.get_risk_level()
            
        total_pressure += seg.pressure
        if "CRITICAL" in status:
            critical_count += 1
            
        clean_water_dist = float(seg.water_dist)

        
        current_data_to_show.append({
            'Segment': seg.segment_id,
            'Distance to Water (m)': seg.water_dist,
            'Pressure (Pa)': seg.pressure,
            'Temperature (°C)': round(seg.temperature, 1),
            'Status': status
        })

        db_logs.append({
            'segment_id': seg.segment_id,
            'pressure': seg.pressure,
            'temperature': round(seg.temperature, 1),
            'water_dist': clean_water_dist,
            'risk_status': status
        })

    
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO sensor_history (segment_id, pressure, temperature, water_dist, risk_status)
                VALUES (:segment_id, :pressure, :temperature, :water_dist, :risk_status);
            """),
            db_logs
        )

    
    with metrics_placeholder.container():
        cols = st.columns(3)
        cols[0].metric('Total Segments (PostGIS DB)', f'{num_segments}')
        cols[1].metric('Average Pressure in System', f'{int(total_pressure / num_segments)} Pa')
        cols[2].metric('Critical Alarms per Second', f'{critical_count}')

    
    table_title_placeholder.markdown('### 📊 Live Data Stream from Sensors (Writing to DB...)')
    df_show = pd.DataFrame(current_data_to_show)
    table_placeholder.dataframe(df_show, use_container_width=True)

    
    history_df = pd.read_sql("""
        SELECT timestamp, segment_id, pressure 
        FROM sensor_history 
        ORDER BY timestamp DESC 
        LIMIT 50
    """, engine)
    
    if not history_df.empty:
        chart_title_placeholder.markdown('### 📈 Historical Pressure Trend (Direct Read from PostgreSQL)')
        chart_data = history_df.pivot(index='timestamp', columns='segment_id', values='pressure')
        chart_placeholder.line_chart(chart_data)

    
    time.sleep(5)
    st.rerun()

else:
    st.warning("⚠️ Pipeline monitoring is disabled. Sensors are not polled, and data writing to the database is suspended.")