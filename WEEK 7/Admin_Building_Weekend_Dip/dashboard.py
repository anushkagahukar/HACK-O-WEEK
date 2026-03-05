"""
Admin Building Weekend Dip - Interactive Dashboard
===================================================
A Streamlit-based dashboard for analyzing energy consumption patterns,
clustering, and forecasting.

Run this dashboard with:
    streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data_loader import EnergyDataLoader
from src.clustering import EnergyClusterer
from src.regression import EnergyRegressor
from src.utils import calculate_savings_potential, print_metrics

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Building Energy Analysis",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    h1 {
        color: #000000;
        text-align: center;
        margin-bottom: 2rem;
    }
    h2 {
        color: #000000;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Configure matplotlib for black text
plt.rcParams['text.color'] = '#000000'
plt.rcParams['axes.labelcolor'] = '#000000'
plt.rcParams['xtick.color'] = '#000000'
plt.rcParams['ytick.color'] = '#000000'
plt.rcParams['axes.edgecolor'] = '#000000'

# ============================================================================
# SIDEBAR - FILE UPLOAD & CONFIGURATION
# ============================================================================

st.sidebar.markdown("# ⚙️ Configuration")
st.sidebar.markdown("---")

# File upload
uploaded_file = st.sidebar.file_uploader(
    "📁 Upload Energy Data (CSV)",
    type=['csv'],
    help="CSV with columns: Date, Day, Hour, Energy_Consumption"
)

# Use sample data option
use_sample = st.sidebar.checkbox("📊 Use Sample Data", value=False)

# Clustering parameters
st.sidebar.markdown("### Clustering Settings")
n_clusters = st.sidebar.slider("Number of Clusters", 2, 5, 3)

# Regression parameters
st.sidebar.markdown("### Forecast Settings")
polynomial_degree = st.sidebar.slider("Polynomial Degree", 1, 3, 2)
forecast_days = st.sidebar.slider("Forecast Days", 7, 90, 30)

st.sidebar.markdown("---")

# Data source info
if uploaded_file:
    data_source = "📤 Uploaded File"
elif use_sample:
    data_source = "📊 Sample Data"
else:
    data_source = "❌ No Data"

st.sidebar.info(f"**Data Source:** {data_source}")

# ============================================================================
# MAIN APP LOGIC
# ============================================================================

@st.cache_resource
def load_and_process_data(filepath=None):
    """Load and process data with caching."""
    
    loader = EnergyDataLoader()
    
    # Load data
    if filepath:
        loader.load_data(filepath)
    else:
        # Try to load from default location
        default_path = 'data/energy_data.csv'
        if os.path.exists(default_path):
            loader.load_data(default_path)
        else:
            return None, None, None
    
    hourly_data = loader.get_hourly_data()
    daily_data = loader.get_daily_data()
    
    # Perform clustering
    clusterer = EnergyClusterer()
    clusterer.fit(daily_data, n_clusters=n_clusters)
    labeled_data = clusterer.get_labeled_data()
    
    # Perform regression
    regressor = EnergyRegressor()
    regressor.fit(labeled_data, degree=polynomial_degree)
    regressor.forecast(days_into_future=forecast_days)
    
    return (hourly_data, daily_data, labeled_data), clusterer, regressor

def main():
    """Main application."""
    
    # Title
    st.markdown("# ⚡ Admin Building Weekend Dip Analysis")
    st.markdown("Energy Consumption Analysis, Clustering & Forecasting Dashboard")
    st.markdown("---")
    
    # Check if data is available
    if not uploaded_file and not use_sample:
        st.warning("⚠️ Please upload a CSV file or enable 'Use Sample Data' in the sidebar.")
        
        st.info("""
        ### Expected Data Format
        Your CSV file should contain the following columns:
        - **Date**: Calendar date (YYYY-MM-DD)
        - **Day**: Day of the week (Monday, Tuesday, etc.)
        - **Hour**: Hour of the day (0-23)
        - **Energy_Consumption**: Energy consumed in kWh (numeric)
        
        Example rows:
        ```
        Date,Day,Hour,Energy_Consumption
        2023-01-01,Sunday,0,18.45
        2023-01-01,Sunday,1,16.82
        2023-01-02,Monday,0,28.34
        ```
        """)
        
        with st.expander("📝 Generate Sample Data"):
            if st.button("Generate Sample Dataset"):
                st.info("Generating sample data...")
                try:
                    from generate_sample_data import generate_sample_data
                    generate_sample_data(num_days=365, output_path='data/energy_data.csv')
                    st.success("✓ Sample data generated! Refresh the page and select 'Use Sample Data'")
                except Exception as e:
                    st.error(f"Error generating sample data: {e}")
        
        return
    
    # Load and process data
    try:
        with st.spinner("📊 Loading and processing data..."):
            if uploaded_file:
                # Save uploaded file temporarily
                with open('temp_data.csv', 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                data_path = 'temp_data.csv'
            else:
                data_path = 'data/energy_data.csv'
            
            # Load data
            loader = EnergyDataLoader()
            loader.load_data(data_path)
            hourly_data = loader.get_hourly_data()
            daily_data = loader.get_daily_data()
            
            # Perform clustering
            clusterer = EnergyClusterer()
            clusterer.fit(daily_data, n_clusters=n_clusters)
            labeled_data = clusterer.get_labeled_data()
            
            # Perform regression
            regressor = EnergyRegressor()
            regressor.fit(labeled_data, degree=polynomial_degree)
            regressor.forecast(days_into_future=forecast_days)
    
    except Exception as e:
        st.error(f"❌ Error processing data: {str(e)}")
        return
    
    # ========================================================================
    # SECTION 1: DATA SUMMARY
    # ========================================================================
    
    col1, col2, col3, col4 = st.columns(4)
    
    stats = loader.get_summary_stats()
    
    with col1:
        st.metric("📅 Total Days", stats['total_days'])
    with col2:
        st.metric("📊 Weekdays", stats['total_weekdays'])
    with col3:
        st.metric("🎉 Weekends", stats['total_weekends'])
    with col4:
        st.metric("⚡ Avg Usage (Hourly)", f"{stats['hourly_mean']:.2f} kWh")
    
    st.markdown("---")
    
    # ========================================================================
    # SECTION 2: CLUSTERING ANALYSIS
    # ========================================================================
    
    st.markdown("## 📍 Clustering Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Visualization
        fig = clusterer.visualize_clusters(figsize=(10, 6))
        st.pyplot(fig, use_container_width=True)
    
    with col2:
        # Cluster summary table
        cluster_info = clusterer.get_cluster_info()
        st.markdown("### Cluster Summary")
        st.dataframe(
            cluster_info[['Usage_Level', 'Count', 'Avg_Daily_Consumption']],
            use_container_width=True,
            hide_index=True
        )
    
    # Pie chart of cluster distribution
    cluster_dist = cluster_info.set_index('Usage_Level')['Count']
    
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = ['#2ecc71', '#f39c12', '#e74c3c']
    wedges, texts, autotexts = ax.pie(
        cluster_dist.values,
        labels=cluster_dist.index,
        autopct='%1.1f%%',
        colors=colors[:len(cluster_dist)],
        startangle=90,
        textprops={'fontsize': 11, 'weight': 'bold', 'color': '#000000'}
    )
    # Ensure all text is black
    for text in texts:
        text.set_color('#000000')
        text.set_fontweight('bold')
        text.set_fontsize(11)
    for autotext in autotexts:
        autotext.set_color('#ffffff')
        autotext.set_fontweight('bold')
    ax.set_title('Cluster Distribution', fontsize=14, fontweight='bold', pad=20, color='#000000')
    
    st.pyplot(fig, use_container_width=True)
    
    st.markdown("---")
    
    # ========================================================================
    # SECTION 3: WEEKDAY VS WEEKEND COMPARISON
    # ========================================================================
    
    st.markdown("## 📊 Weekday vs Weekend Comparison")
    
    weekday_data = daily_data[daily_data['Day_Type'] == 'Weekday']
    weekend_data = daily_data[daily_data['Day_Type'] == 'Weekend']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📈 Weekday Avg",
            f"{weekday_data['Daily_Avg'].mean():.2f} kWh"
        )
    with col2:
        st.metric(
            "📉 Weekend Avg",
            f"{weekend_data['Daily_Avg'].mean():.2f} kWh"
        )
    with col3:
        dip_pct = (
            (weekday_data['Daily_Avg'].mean() - weekend_data['Daily_Avg'].mean()) /
            weekday_data['Daily_Avg'].mean() * 100
        )
        st.metric(
            "📊 Weekend Dip",
            f"{dip_pct:.2f}%"
        )
    with col4:
        savings = (
            weekday_data['Daily_Avg'].mean() - weekend_data['Daily_Avg'].mean()
        )
        st.metric(
            "💰 Savings Potential",
            f"{savings:.2f} kWh"
        )
    
    # Bar chart comparing usage
    compare_data = pd.DataFrame({
        'Weekday': [weekday_data['Daily_Avg'].mean()],
        'Weekend': [weekend_data['Daily_Avg'].mean()]
    })
    
    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(compare_data.columns))
    bars = ax.bar(x, compare_data.values[0], color=['#3498db', '#2ecc71'], alpha=0.8, width=0.5)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{height:.2f}',
               ha='center', va='bottom', fontsize=12, fontweight='bold', color='#000000')
    
    ax.set_ylabel('Average Daily Consumption (kWh)', fontsize=11, fontweight='bold', color='#000000')
    ax.set_title('Weekday vs Weekend Energy Consumption', fontsize=13, fontweight='bold', color='#000000')
    ax.set_xticks(x)
    ax.set_xticklabels(compare_data.columns, color='#000000')
    ax.tick_params(colors='#000000')
    ax.grid(axis='y', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    st.pyplot(fig, use_container_width=True)
    
    st.markdown("---")
    
    # ========================================================================
    # SECTION 4: FORECASTING
    # ========================================================================
    
    st.markdown("## 🔮 Energy Forecasting")
    
    st.info(
        f"Forecast based on Polynomial Regression (degree={polynomial_degree}) "
        f"for the next {forecast_days} days"
    )
    
    # Visualization
    fig = regressor.visualize_forecasts(labeled_data, figsize=(14, 10))
    st.pyplot(fig, use_container_width=True)
    
    # Forecast metrics
    st.markdown("### Forecast Summary by Cluster")
    
    forecasts = regressor.get_forecasts()
    metrics = regressor.get_metrics()
    
    forecast_summary = []
    for cluster in forecasts.keys():
        forecast_summary.append({
            'Cluster': cluster,
            'Mean Forecast (kWh)': forecasts[cluster]['mean_forecast'],
            'Trend': forecasts[cluster]['trend'].title(),
            'R² Score': metrics[cluster]['r2_score'],
            'RMSE (kWh)': metrics[cluster]['rmse']
        })
    
    forecast_df = pd.DataFrame(forecast_summary)
    st.dataframe(forecast_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # ========================================================================
    # SECTION 5: SAVINGS POTENTIAL
    # ========================================================================
    
    st.markdown("## 💰 Savings Potential Analysis")
    
    # Calculate savings metrics
    weekday_avg = weekday_data['Daily_Avg'].mean()
    weekend_avg = weekend_data['Daily_Avg'].mean()
    
    savings = calculate_savings_potential(weekday_avg, weekend_avg)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Current Usage")
        st.metric("Weekday Average", f"{savings['weekday_avg']:.2f} kWh")
        st.metric("Weekend Average", f"{savings['weekend_avg']:.2f} kWh")
        st.metric("Weekend Dip", f"{savings['dip_percentage']:.2f}%", delta=f"-{savings['dip_percentage']:.2f}%")
    
    with col2:
        st.markdown("### Savings Potential")
        st.metric("Weekday Savings", f"{savings['weekday_savings_potential']:.2f} kWh", 
                 delta=f"{savings['weekday_savings_pct']:.2f}%")
        st.metric("Weekend Savings", f"{savings['weekend_savings_potential']:.2f} kWh",
                 delta=f"{savings['weekend_savings_pct']:.2f}%")
        st.metric("Target Usage", f"{savings['target_usage']:.2f} kWh")
    
    # Detailed savings table
    st.markdown("### Detailed Savings Metrics")
    
    savings_table = pd.DataFrame({
        'Metric': ['Weekday Avg Usage', 'Weekend Avg Usage', 'Target Usage Level',
                   'Weekday Savings', 'Weekend Savings'],
        'Value (kWh)': [
            savings['weekday_avg'],
            savings['weekend_avg'],
            savings['target_usage'],
            savings['weekday_savings_potential'],
            savings['weekend_savings_potential']
        ],
        'Percentage': [
            '-',
            f"-{savings['dip_percentage']:.2f}%",
            '-',
            f"{savings['weekday_savings_pct']:.2f}%",
            f"{savings['weekend_savings_pct']:.2f}%"
        ]
    })
    
    st.dataframe(savings_table, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # ========================================================================
    # SECTION 6: DETAILED DATA VIEW
    # ========================================================================
    
    st.markdown("## 📋 Detailed Data View")
    
    tabs = st.tabs(["Daily Summary", "Daily Details", "Cluster Analysis", "Hourly Data"])
    
    with tabs[0]:
        st.markdown("### Daily Summary (First 50 days)")
        st.dataframe(
            daily_data.head(50)[['Date', 'Day', 'Day_Type', 'Daily_Total', 'Daily_Avg']],
            use_container_width=True,
            hide_index=True
        )
    
    with tabs[1]:
        st.markdown("### Daily Details with Cluster Assignment")
        st.dataframe(
            labeled_data.head(50)[['Date', 'Day', 'Day_Type', 'Daily_Avg', 'Usage_Level']],
            use_container_width=True,
            hide_index=True
        )
    
    with tabs[2]:
        st.markdown("### Cluster Characteristics")
        cluster_info = clusterer.get_cluster_info()
        st.dataframe(cluster_info, use_container_width=True, hide_index=True)
    
    with tabs[3]:
        st.markdown("### Hourly Data (First 100 records)")
        st.dataframe(
            hourly_data.head(100),
            use_container_width=True,
            hide_index=True
        )
    
    # ========================================================================
    # FOOTER
    # ========================================================================
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #7f8c8d; font-size: 12px; padding: 20px;'>
    <p>Admin Building Weekend Dip Analysis Dashboard v1.0</p>
    <p>Energy consumption analysis with K-Means clustering and polynomial regression forecasting</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
