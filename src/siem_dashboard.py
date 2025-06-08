import streamlit as st
import pandas as pd
import json
import plotly.express as px
from datetime import datetime, timedelta
import altair as alt
from pathlib import Path
import time

# Set page config
st.set_page_config(
    page_title="SIEM Dashboard",
    page_icon="🔒",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #0E1117;
    }
    .stAlert {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .metric-card {
        background-color: #1E2130;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

def load_logs():
    """Load and parse log files"""
    log_path = Path("logs/sample.log")
    if not log_path.exists():
        return pd.DataFrame()
    
    logs = []
    with open(log_path) as f:
        for line in f:
            try:
                timestamp, level, message = line.strip().split(" ", 2)
                logs.append({
                    "timestamp": datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S"),
                    "level": level,
                    "message": message
                })
            except:
                continue
    
    return pd.DataFrame(logs)

def load_detections():
    """Load detection results"""
    detection_files = list(Path("logs").glob("detections_*.json"))
    if not detection_files:
        return pd.DataFrame()
    
    latest_file = max(detection_files, key=lambda x: x.stat().st_mtime)
    with open(latest_file) as f:
        return pd.DataFrame(json.load(f))

def create_alert_chart(df):
    """Create alert severity chart"""
    if df.empty:
        return None
    
    severity_counts = df['severity'].value_counts().reset_index()
    severity_counts.columns = ['severity', 'count']
    
    fig = px.bar(
        severity_counts,
        x='severity',
        y='count',
        color='severity',
        title='Alert Severity Distribution',
        color_discrete_map={
            'critical': 'red',
            'high': 'orange',
            'medium': 'yellow',
            'low': 'green'
        }
    )
    return fig

def create_timeline_chart(df):
    """Create timeline chart of events"""
    if df.empty:
        return None
    
    df['hour'] = df['timestamp'].dt.hour
    hourly_counts = df.groupby('hour').size().reset_index(name='count')
    
    fig = px.line(
        hourly_counts,
        x='hour',
        y='count',
        title='Events Timeline',
        labels={'hour': 'Hour of Day', 'count': 'Number of Events'}
    )
    return fig

def main():
    st.title("🔒 SIEM Dashboard")
    
    # Sidebar
    st.sidebar.title("Settings")
    refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 5, 60, 10)
    
    # Main content
    col1, col2, col3 = st.columns(3)
    
    # Load data
    logs_df = load_logs()
    detections_df = load_detections()
    
    # Metrics
    with col1:
        st.metric("Total Events", len(logs_df))
    with col2:
        st.metric("Alerts", len(detections_df))
    with col3:
        if not logs_df.empty:
            st.metric("Latest Event", logs_df['timestamp'].max().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        if not detections_df.empty:
            st.plotly_chart(create_alert_chart(detections_df), use_container_width=True)
    
    with col2:
        if not logs_df.empty:
            st.plotly_chart(create_timeline_chart(logs_df), use_container_width=True)
    
    # Recent Events
    st.subheader("Recent Events")
    if not logs_df.empty:
        st.dataframe(
            logs_df.sort_values('timestamp', ascending=False).head(10),
            use_container_width=True
        )
    
    # Alerts
    st.subheader("Active Alerts")
    if not detections_df.empty:
        st.dataframe(
            detections_df.sort_values('timestamp', ascending=False).head(10),
            use_container_width=True
        )
    
    # Auto-refresh
    time.sleep(refresh_interval)
    st.rerun()

if __name__ == "__main__":
    main() 