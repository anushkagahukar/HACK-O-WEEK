import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# Set page configuration
st.set_page_config(
    page_title="DC Weather Analysis Dashboard",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('dc_weather.csv')
    df['datetime'] = pd.to_datetime(df['datetime'])
    return df

df = load_data()

# Sidebar
st.sidebar.header("📊 Dashboard Controls")
analysis_type = st.sidebar.selectbox(
    "Select Analysis Type",
    ["Overview", "Temperature Analysis", "Precipitation Analysis", "Wind Analysis", "Climate Patterns", "Comparative Analysis"]
)

date_range = st.sidebar.slider(
    "Select Date Range",
    min_value=df['datetime'].min().date(),
    max_value=df['datetime'].max().date(),
    value=(df['datetime'].min().date(), df['datetime'].max().date())
)

# Filter data by date range
df_filtered = df[(df['datetime'].dt.date >= date_range[0]) & (df['datetime'].dt.date <= date_range[1])]

# Title
st.title("🌤️ Washington DC Weather Analysis Dashboard")
st.markdown(f"**Analysis Period:** {date_range[0]} to {date_range[1]} | **Total Records:** {len(df_filtered)}")

# ==================== OVERVIEW ====================
if analysis_type == "Overview":
    st.header("📈 Weather Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Avg Temperature (°C)", f"{df_filtered['temp'].mean():.1f}")
    with col2:
        st.metric("Max Temperature (°C)", f"{df_filtered['tempmax'].max():.1f}")
    with col3:
        st.metric("Min Temperature (°C)", f"{df_filtered['tempmin'].min():.1f}")
    with col4:
        st.metric("Avg Humidity (%)", f"{df_filtered['humidity'].mean():.1f}")
    
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric("Total Precipitation (mm)", f"{df_filtered['precip'].sum():.1f}")
    with col6:
        st.metric("Rainy Days", f"{(df_filtered['precip'] > 0).sum()}")
    with col7:
        st.metric("Avg Wind Speed (km/h)", f"{df_filtered['windspeed'].mean():.1f}")
    with col8:
        st.metric("Avg Cloud Cover (%)", f"{df_filtered['cloudcover'].mean():.1f}")
    
    st.divider()
    
    # Weather conditions distribution
    st.subheader("🌦️ Weather Conditions Distribution")
    conditions_count = df_filtered['conditions'].value_counts().head(10)
    
    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots(figsize=(10, 5))
        conditions_count.plot(kind='barh', ax=ax, color='steelblue')
        ax.set_xlabel("Number of Days")
        ax.set_title("Top 10 Weather Conditions")
        st.pyplot(fig)
    
    with col2:
        fig = px.pie(values=conditions_count.values, names=conditions_count.index, 
                     title="Weather Conditions Pie Chart")
        st.plotly_chart(fig, use_container_width=True)

# ==================== TEMPERATURE ANALYSIS ====================
elif analysis_type == "Temperature Analysis":
    st.header("🌡️ Temperature Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Average Temperature", f"{df_filtered['temp'].mean():.1f}°C")
        st.metric("Max Temperature", f"{df_filtered['tempmax'].max():.1f}°C")
        st.metric("Min Temperature", f"{df_filtered['tempmin'].min():.1f}°C")
    
    with col2:
        st.metric("Temperature Std Dev", f"{df_filtered['temp'].std():.1f}°C")
        st.metric("Average Feels Like", f"{df_filtered['feelslike'].mean():.1f}°C")
        st.metric("Dew Point Avg", f"{df_filtered['dew'].mean():.1f}°C")
    
    st.divider()
    
    # Temperature trends
    st.subheader("📊 Temperature Trends Over Time")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_filtered['datetime'], y=df_filtered['temp'],
                             mode='lines', name='Average Temp', line=dict(color='orange', width=2)))
    fig.add_trace(go.Scatter(x=df_filtered['datetime'], y=df_filtered['tempmax'],
                             mode='lines', name='Max Temp', line=dict(color='red', width=1, dash='dash')))
    fig.add_trace(go.Scatter(x=df_filtered['datetime'], y=df_filtered['tempmin'],
                             mode='lines', name='Min Temp', line=dict(color='blue', width=1, dash='dash')))
    fig.update_layout(title="Temperature Trends", xaxis_title="Date", yaxis_title="Temperature (°C)",
                      hovermode='x unified', height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        # Temperature distribution
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(df_filtered['temp'], bins=30, color='steelblue', edgecolor='black', alpha=0.7)
        ax.set_xlabel("Temperature (°C)")
        ax.set_ylabel("Frequency")
        ax.set_title("Temperature Distribution")
        st.pyplot(fig)
    
    with col2:
        # Feels like vs actual
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.scatter(df_filtered['temp'], df_filtered['feelslike'], alpha=0.6, color='coral')
        ax.plot([df_filtered['temp'].min(), df_filtered['temp'].max()], 
                [df_filtered['temp'].min(), df_filtered['temp'].max()], 'k--', lw=2)
        ax.set_xlabel("Actual Temperature (°C)")
        ax.set_ylabel("Feels Like Temperature (°C)")
        ax.set_title("Actual vs Feels Like Temperature")
        st.pyplot(fig)

# ==================== PRECIPITATION ANALYSIS ====================
elif analysis_type == "Precipitation Analysis":
    st.header("🌧️ Precipitation Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Precipitation", f"{df_filtered['precip'].sum():.2f} mm")
        st.metric("Rainy Days", f"{(df_filtered['precip'] > 0).sum()}")
        st.metric("Max Daily Precip", f"{df_filtered['precip'].max():.2f} mm")
    
    with col2:
        st.metric("Avg Precip (Rainy Days)", f"{df_filtered[df_filtered['precip'] > 0]['precip'].mean():.2f} mm")
        st.metric("Avg Precip Probability", f"{df_filtered['precipprob'].mean():.1f}%")
        st.metric("Days with Snow", f"{(df_filtered['snow'] > 0).sum()}")
    
    st.divider()
    
    # Precipitation trends
    st.subheader("📈 Precipitation Over Time")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_filtered['datetime'], y=df_filtered['precip'],
                        marker_color='lightblue', name='Precipitation'))
    fig.update_layout(title="Daily Precipitation", xaxis_title="Date", yaxis_title="Precipitation (mm)",
                      height=500, hovermode='x')
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        # Precipitation distribution
        fig, ax = plt.subplots(figsize=(10, 5))
        precip_data = df_filtered[df_filtered['precip'] > 0]['precip']
        ax.hist(precip_data, bins=30, color='steelblue', edgecolor='black', alpha=0.7)
        ax.set_xlabel("Precipitation (mm)")
        ax.set_ylabel("Frequency")
        ax.set_title("Precipitation Distribution (Rainy Days Only)")
        st.pyplot(fig)
    
    with col2:
        # Precipitation vs Humidity
        fig, ax = plt.subplots(figsize=(10, 5))
        scatter = ax.scatter(df_filtered['precip'], df_filtered['humidity'], 
                            c=df_filtered['temp'], cmap='viridis', alpha=0.6, s=30)
        ax.set_xlabel("Precipitation (mm)")
        ax.set_ylabel("Humidity (%)")
        ax.set_title("Precipitation vs Humidity (colored by Temp)")
        plt.colorbar(scatter, ax=ax, label='Temperature (°C)')
        st.pyplot(fig)
    
    st.divider()
    st.subheader("🌧️ Precipitation Type Distribution")
    precip_types = df_filtered[df_filtered['preciptype'].notna()]['preciptype'].value_counts()
    if len(precip_types) > 0:
        fig = px.pie(values=precip_types.values, names=precip_types.index,
                     title="Types of Precipitation")
        st.plotly_chart(fig, use_container_width=True)

# ==================== WIND ANALYSIS ====================
elif analysis_type == "Wind Analysis":
    st.header("💨 Wind Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Avg Wind Speed", f"{df_filtered['windspeed'].mean():.1f} km/h")
        st.metric("Max Wind Gust", f"{df_filtered['windgust'].max():.1f} km/h")
        st.metric("Min Wind Speed", f"{df_filtered['windspeed'].min():.1f} km/h")
    
    with col2:
        st.metric("Wind Speed Std Dev", f"{df_filtered['windspeed'].std():.1f} km/h")
        st.metric("Avg Wind Direction", f"{df_filtered['winddir'].mean():.1f}°")
        st.metric("Total Days Recorded", f"{len(df_filtered)}")
    
    st.divider()
    
    # Wind speed trends
    st.subheader("📊 Wind Speed Trends")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_filtered['datetime'], y=df_filtered['windspeed'],
                             mode='lines', name='Wind Speed', line=dict(color='steelblue', width=2)))
    fig.add_trace(go.Scatter(x=df_filtered['datetime'], y=df_filtered['windgust'],
                             mode='lines', name='Wind Gust', line=dict(color='red', width=1, dash='dash')))
    fig.update_layout(title="Wind Speed Trends Over Time", xaxis_title="Date", yaxis_title="Speed (km/h)",
                      hovermode='x unified', height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        # Wind speed distribution
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(df_filtered['windspeed'], bins=30, color='steelblue', edgecolor='black', alpha=0.7)
        ax.set_xlabel("Wind Speed (km/h)")
        ax.set_ylabel("Frequency")
        ax.set_title("Wind Speed Distribution")
        st.pyplot(fig)
    
    with col2:
        # Wind direction polar plot
        fig = go.Figure(go.Barpolar(
            r=np.ones(len(df_filtered)),
            theta=df_filtered['winddir'],
            marker=dict(color=df_filtered['windspeed'], colorscale='Viridis'),
            name='Wind'
        ))
        fig.update_layout(title="Wind Direction Distribution", height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    st.subheader("💨 Wind Speed vs Temperature")
    fig, ax = plt.subplots(figsize=(12, 6))
    scatter = ax.scatter(df_filtered['temp'], df_filtered['windspeed'],
                        c=df_filtered['humidity'], cmap='plasma', alpha=0.6, s=50)
    ax.set_xlabel("Temperature (°C)")
    ax.set_ylabel("Wind Speed (km/h)")
    ax.set_title("Wind Speed vs Temperature (colored by Humidity)")
    plt.colorbar(scatter, ax=ax, label='Humidity (%)')
    st.pyplot(fig)

# ==================== CLIMATE PATTERNS ====================
elif analysis_type == "Climate Patterns":
    st.header("🔄 Climate Patterns & Seasonality")
    
    df_filtered['month'] = df_filtered['datetime'].dt.month
    df_filtered['month_name'] = df_filtered['datetime'].dt.strftime('%B')
    
    # Monthly statistics
    st.subheader("📊 Monthly Climate Statistics")
    monthly_stats = df_filtered.groupby('month_name').agg({
        'temp': 'mean',
        'tempmax': 'max',
        'tempmin': 'min',
        'humidity': 'mean',
        'precip': 'sum',
        'windspeed': 'mean'
    }).round(2)
    
    st.dataframe(monthly_stats, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        # Monthly temperature boxplot
        fig, ax = plt.subplots(figsize=(12, 6))
        df_filtered.boxplot(column='temp', by='month_name', ax=ax)
        ax.set_xlabel("Month")
        ax.set_ylabel("Temperature (°C)")
        ax.set_title("Temperature Distribution by Month")
        plt.suptitle("")
        st.pyplot(fig)
    
    with col2:
        # Monthly precipitation
        monthly_precip = df_filtered.groupby('month_name')['precip'].sum()
        fig, ax = plt.subplots(figsize=(12, 6))
        monthly_precip.plot(kind='bar', ax=ax, color='steelblue')
        ax.set_xlabel("Month")
        ax.set_ylabel("Total Precipitation (mm)")
        ax.set_title("Total Monthly Precipitation")
        plt.xticks(rotation=45)
        st.pyplot(fig)
    
    st.divider()
    
    # Humidity patterns
    st.subheader("💧 Humidity Patterns")
    fig = go.Figure()
    for month in sorted(df_filtered['month'].unique()):
        month_data = df_filtered[df_filtered['month'] == month]
        fig.add_trace(go.Box(y=month_data['humidity'], name=month_data['month_name'].iloc[0]))
    
    fig.update_layout(title="Humidity Distribution by Month", yaxis_title="Humidity (%)", height=500)
    st.plotly_chart(fig, use_container_width=True)

# ==================== COMPARATIVE ANALYSIS ====================
elif analysis_type == "Comparative Analysis":
    st.header("📊 Comparative Analysis")
    
    # Correlation heatmap
    st.subheader("🔗 Feature Correlation Matrix")
    
    numeric_cols = ['temp', 'tempmax', 'tempmin', 'humidity', 'precip', 'windspeed', 
                    'windgust', 'sealevelpressure', 'cloudcover', 'visibility', 'uvindex', 'dew']
    
    correlation_matrix = df_filtered[numeric_cols].corr()
    
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                square=True, ax=ax, cbar_kws={'label': 'Correlation'})
    ax.set_title("Feature Correlation Matrix")
    st.pyplot(fig)
    
    st.divider()
    
    # Create categories for comparison
    st.subheader("📈 Comparative Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    # Pressure vs Temperature
    with col1:
        fig, ax = plt.subplots(figsize=(8, 5))
        scatter = ax.scatter(df_filtered['sealevelpressure'], df_filtered['temp'],
                            c=df_filtered['humidity'], cmap='RdYlGn_r', alpha=0.6, s=30)
        ax.set_xlabel("Sea Level Pressure (hPa)")
        ax.set_ylabel("Temperature (°C)")
        ax.set_title("Pressure vs Temperature")
        plt.colorbar(scatter, ax=ax, label='Humidity (%)')
        st.pyplot(fig)
    
    # Visibility vs Humidity
    with col2:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.scatter(df_filtered['humidity'], df_filtered['visibility'],
                  c=df_filtered['cloudcover'], cmap='viridis', alpha=0.6, s=30)
        ax.set_xlabel("Humidity (%)")
        ax.set_ylabel("Visibility (km)")
        ax.set_title("Humidity vs Visibility")
        st.pyplot(fig)
    
    # UV Index vs Temperature
    with col3:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.scatter(df_filtered['temp'], df_filtered['uvindex'],
                  c=df_filtered['cloudcover'], cmap='plasma', alpha=0.6, s=30)
        ax.set_xlabel("Temperature (°C)")
        ax.set_ylabel("UV Index")
        ax.set_title("Temperature vs UV Index")
        st.pyplot(fig)
    
    st.divider()
    
    # Summary statistics table
    st.subheader("📋 Summary Statistics")
    summary_stats = df_filtered[numeric_cols].describe().round(2)
    st.dataframe(summary_stats, use_container_width=True)

# Footer
st.divider()
st.markdown("""
---
**Dashboard Created with Streamlit** | 
Data Source: Washington DC Weather (2015-Present) | 
Last Updated: January 2026
""")
