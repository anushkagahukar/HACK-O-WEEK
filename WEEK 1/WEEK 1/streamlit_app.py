import streamlit as st
import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Electricity Apartment Analysis",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 0rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# LOAD DATA
# ============================================================================
@st.cache_data
def load_data():
    csv_path = r'electricity_apartment-summary.csv'
    df = pd.read_csv(csv_path, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    
    json_path = r'electricity_apartment-group_details.json'
    with open(json_path, 'r') as f:
        group_details = json.load(f)
    
    return df, group_details

df, group_details = load_data()

# Extract time components
df['hour'] = df.index.hour
df['date'] = df.index.date
df['day_of_week'] = df.index.day_name()
df['month'] = df.index.month

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================
st.sidebar.title("📊 Navigation")
page = st.sidebar.radio(
    "Select Section:",
    ["🏠 Dashboard", "📈 Analysis", "📊 Statistics", "🔍 Patterns", "👥 Demographics"]
)

# ============================================================================
# DASHBOARD PAGE
# ============================================================================
if page == "🏠 Dashboard":
    st.title("⚡ Electricity Apartment Consumption Dashboard")
    st.markdown("---")
    
    # Key Metrics Row 1
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📅 Total Records",
            f"{len(df):,}",
            f"{(df.index.max() - df.index.min()).days} days"
        )
    
    with col2:
        st.metric(
            "🏢 Apartments Monitored",
            int(df['Count'].iloc[0]),
            "67 units"
        )
    
    with col3:
        st.metric(
            "⚡ Avg Daily Consumption",
            f"{df.groupby('date')['Mean'].sum().mean():.0f} Wh",
            f"Per apt: {df.groupby('date')['Mean'].sum().mean()/67:.0f} Wh"
        )
    
    with col4:
        st.metric(
            "📊 Peak Consumption",
            f"{df['Max'].max():.0f} Wh",
            f"Variation: {df['Max'].max()/df['Min'].min():.0f}x"
        )
    
    st.markdown("---")
    
    # Time Series Visualization
    st.subheader("📈 Consumption Trend Over Time")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Mean'],
        name='Mean', line=dict(color='#667eea', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Max'],
        name='Max', line=dict(color='#FF6B6B', width=1, dash='dash'),
        fill=None
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Min'],
        name='Min', line=dict(color='#51CF66', width=1, dash='dash'),
        fill='tonexty'
    ))
    
    fig.update_layout(
        title='Consumption Range and Trends',
        xaxis_title='Date',
        yaxis_title='Consumption (Wh)',
        hovermode='x unified',
        height=400,
        template='plotly_dark'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Hourly and Daily Patterns
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⏰ Hourly Consumption Pattern")
        hourly_data = df.groupby('hour')['Mean'].mean()
        fig_hourly = px.bar(
            x=hourly_data.index,
            y=hourly_data.values,
            labels={'x': 'Hour of Day', 'y': 'Consumption (Wh)'},
            title='Average Consumption by Hour',
            color=hourly_data.values,
            color_continuous_scale='Viridis'
        )
        fig_hourly.update_layout(height=400, showlegend=False, template='plotly_dark')
        st.plotly_chart(fig_hourly, use_container_width=True)
    
    with col2:
        st.subheader("📅 Weekly Consumption Pattern")
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekly_data = df.groupby('day_of_week')['Mean'].mean().reindex(day_order)
        colors = ['#FF6B6B' if day in ['Saturday', 'Sunday'] else '#667eea' for day in day_order]
        fig_weekly = px.bar(
            x=day_order,
            y=weekly_data.values,
            labels={'x': 'Day', 'y': 'Consumption (Wh)'},
            title='Average Consumption by Day',
            color=colors
        )
        fig_weekly.update_layout(height=400, showlegend=False, template='plotly_dark')
        st.plotly_chart(fig_weekly, use_container_width=True)

# ============================================================================
# ANALYSIS PAGE
# ============================================================================
elif page == "📈 Analysis":
    st.title("📈 Detailed Analysis")
    st.markdown("---")
    
    # Tabs for different analyses
    tab1, tab2, tab3 = st.tabs(["Time Series", "Distribution", "Variability"])
    
    with tab1:
        st.subheader("Time Series Decomposition")
        
        # Daily aggregation
        daily_data = df.groupby('date').agg({
            'Mean': ['sum', 'mean', 'min', 'max'],
            'Median': 'mean',
            'Max': 'max',
            'Min': 'min'
        }).reset_index()
        daily_data.columns = ['date', 'total', 'daily_mean', 'daily_min', 'daily_max', 'daily_median', 'max_val', 'min_val']
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily_data['date'], y=daily_data['total'],
            name='Daily Total', fill='tozeroy', line=dict(color='#667eea')
        ))
        fig.update_layout(
            title='Daily Total Consumption',
            xaxis_title='Date',
            yaxis_title='Total Consumption (Wh)',
            height=400,
            template='plotly_dark'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Monthly trend
        monthly_data = df.groupby(df.index.to_period('M')).agg({
            'Mean': ['sum', 'mean']
        }).reset_index()
        monthly_data.columns = ['month', 'total', 'mean']
        monthly_data['month'] = monthly_data['month'].astype(str)
        
        fig_monthly = px.line(
            monthly_data,
            x='month', y='total',
            markers=True,
            title='Monthly Consumption Trend',
            labels={'month': 'Month', 'total': 'Total Consumption (Wh)'}
        )
        fig_monthly.update_layout(height=400, template='plotly_dark')
        st.plotly_chart(fig_monthly, use_container_width=True)
    
    with tab2:
        st.subheader("Distribution Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_hist = px.histogram(
                df, x='Mean',
                nbins=50,
                title='Consumption Distribution',
                labels={'Mean': 'Consumption (Wh)'},
                color_discrete_sequence=['#667eea']
            )
            fig_hist.update_layout(height=400, template='plotly_dark')
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            fig_box = px.box(
                df[['Min', 'Mean', 'Median', 'Max']],
                title='Consumption Metrics Box Plot',
                labels={'value': 'Consumption (Wh)', 'variable': 'Metric'}
            )
            fig_box.update_layout(height=400, template='plotly_dark')
            st.plotly_chart(fig_box, use_container_width=True)
        
        # Statistics
        st.subheader("Distribution Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Skewness", f"{df['Mean'].skew():.4f}")
        with col2:
            st.metric("Kurtosis", f"{df['Mean'].kurtosis():.4f}")
        with col3:
            st.metric("Coef. of Variation", f"{df['Mean'].std() / df['Mean'].mean():.4f}")
    
    with tab3:
        st.subheader("Consumption Variability")
        
        df['Range'] = df['Max'] - df['Min']
        daily_range = df.groupby('date')['Range'].mean()
        
        fig_range = px.line(
            x=daily_range.index, y=daily_range.values,
            title='Daily Consumption Variability (Max - Min)',
            labels={'x': 'Date', 'y': 'Range (Wh)'},
            markers=True
        )
        fig_range.update_layout(height=400, template='plotly_dark')
        st.plotly_chart(fig_range, use_container_width=True)
        
        # Peak vs Off-peak
        st.subheader("Peak vs Off-Peak Analysis")
        peak_hours = [8, 9, 10, 11, 12, 18, 19, 20, 21]
        peak_consumption = df[df['hour'].isin(peak_hours)]['Mean'].mean()
        off_peak_consumption = df[~df['hour'].isin(peak_hours)]['Mean'].mean()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Peak Hours Avg", f"{peak_consumption:.2f} Wh", "(8-12, 18-21)")
        with col2:
            st.metric("Off-Peak Avg", f"{off_peak_consumption:.2f} Wh")
        with col3:
            st.metric("Peak/Off-Peak Ratio", f"{peak_consumption/off_peak_consumption:.2f}x")

# ============================================================================
# STATISTICS PAGE
# ============================================================================
elif page == "📊 Statistics":
    st.title("📊 Statistical Summary")
    st.markdown("---")
    
    # Overall Statistics
    st.subheader("Overall Consumption Statistics (Wh)")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Mean", f"{df['Mean'].mean():.2f}")
    with col2:
        st.metric("Median", f"{df['Mean'].median():.2f}")
    with col3:
        st.metric("Std Dev", f"{df['Mean'].std():.2f}")
    with col4:
        st.metric("Range", f"{df['Mean'].max() - df['Mean'].min():.2f}")
    
    st.markdown("---")
    
    # Quartile Statistics
    st.subheader("Quartile Analysis")
    q1, q2, q3 = df['Mean'].quantile([0.25, 0.5, 0.75])
    iqr = q3 - q1
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Q1 (25%)", f"{q1:.2f} Wh")
    with col2:
        st.metric("Q2 (50%)", f"{q2:.2f} Wh")
    with col3:
        st.metric("Q3 (75%)", f"{q3:.2f} Wh")
    with col4:
        st.metric("IQR", f"{iqr:.2f} Wh")
    
    st.markdown("---")
    
    # Min/Max/Peak analysis
    st.subheader("Consumption Range Statistics")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Min Consumption", f"{df['Min'].min():.2f} Wh")
    with col2:
        st.metric("Max Consumption", f"{df['Max'].max():.2f} Wh")
    with col3:
        st.metric("Avg Max Reading", f"{df['Max'].mean():.2f} Wh")
    
    st.markdown("---")
    
    # Outlier Analysis
    st.subheader("Outlier Detection")
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    outliers = df[(df['Mean'] < lower_bound) | (df['Mean'] > upper_bound)]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Outliers Count", len(outliers))
    with col2:
        st.metric("Outlier %", f"{len(outliers)/len(df)*100:.2f}%")
    with col3:
        st.metric("Bounds", f"{lower_bound:.2f} - {upper_bound:.2f}")

# ============================================================================
# PATTERNS PAGE
# ============================================================================
elif page == "🔍 Patterns":
    st.title("🔍 Consumption Patterns")
    st.markdown("---")
    
    # Hourly patterns
    st.subheader("⏰ Hourly Patterns")
    hourly_stats = df.groupby('hour')['Mean'].agg(['mean', 'min', 'max', 'std'])
    peak_hour = hourly_stats['mean'].idxmax()
    low_hour = hourly_stats['mean'].idxmin()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Peak Hour", f"{peak_hour:02d}:00", f"{hourly_stats.loc[peak_hour, 'mean']:.2f} Wh")
    with col2:
        st.metric("Low Hour", f"{low_hour:02d}:00", f"{hourly_stats.loc[low_hour, 'mean']:.2f} Wh")
    with col3:
        st.metric("Peak/Low Ratio", f"{hourly_stats.loc[peak_hour, 'mean'] / hourly_stats.loc[low_hour, 'mean']:.2f}x")
    
    st.markdown("---")
    
    # Interactive hourly heatmap
    st.subheader("Hourly Consumption Heatmap")
    
    pivot_hourly = df.pivot_table(
        values='Mean', 
        index='hour', 
        columns=df.index.to_period('W').astype(str),
        aggfunc='mean'
    )
    
    fig_heatmap = px.imshow(
        pivot_hourly,
        labels=dict(x="Week", y="Hour", color="Consumption (Wh)"),
        title="Hourly Consumption Heatmap",
        color_continuous_scale="RdYlGn_r",
        height=600
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    st.markdown("---")
    
    # Daily and Weekly patterns
    st.subheader("📅 Weekly Patterns")
    
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekly_stats = df.groupby('day_of_week')['Mean'].agg(['mean', 'std']).reindex(day_order)
    
    fig_weekly_detail = go.Figure()
    fig_weekly_detail.add_trace(go.Scatter(
        x=day_order, y=weekly_stats['mean'],
        error_y=dict(type='data', array=weekly_stats['std']),
        mode='lines+markers',
        name='Mean ± Std Dev',
        line=dict(color='#667eea', width=3),
        marker=dict(size=10)
    ))
    fig_weekly_detail.update_layout(
        title='Weekly Pattern with Variability',
        xaxis_title='Day',
        yaxis_title='Consumption (Wh)',
        height=400,
        template='plotly_dark'
    )
    st.plotly_chart(fig_weekly_detail, use_container_width=True)
    
    # Statistics table
    st.subheader("Weekly Statistics Table")
    st.dataframe(
        weekly_stats.round(2),
        use_container_width=True
    )

# ============================================================================
# DEMOGRAPHICS PAGE
# ============================================================================
elif page == "👥 Demographics":
    st.title("👥 Group Demographics & Characteristics")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Socio-Economic Categories")
        socio_data = pd.DataFrame.from_dict(
            group_details['socioCat'], 
            orient='index', 
            columns=['Count']
        ).sort_values('Count', ascending=False)
        
        fig_socio = px.bar(
            socio_data,
            y=socio_data.index,
            x='Count',
            orientation='h',
            title='Socio-Economic Distribution',
            color='Count',
            color_continuous_scale='Blues'
        )
        fig_socio.update_layout(height=400, template='plotly_dark')
        st.plotly_chart(fig_socio, use_container_width=True)
    
    with col2:
        st.subheader("Dwelling Ownership")
        ownership_data = pd.DataFrame.from_dict(
            group_details['dwelling ownership'],
            orient='index',
            columns=['Count']
        ).sort_values('Count', ascending=False)
        
        fig_ownership = px.pie(
            ownership_data,
            names=ownership_data.index,
            values='Count',
            title='Dwelling Ownership Distribution',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_ownership.update_layout(height=400, template='plotly_dark')
        st.plotly_chart(fig_ownership, use_container_width=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Place Location")
        location_data = pd.DataFrame.from_dict(
            group_details['placeLocation'],
            orient='index',
            columns=['Count']
        ).sort_values('Count', ascending=False)
        
        fig_location = px.bar(
            location_data,
            y=location_data.index,
            x='Count',
            orientation='h',
            title='Location Distribution',
            color='Count',
            color_continuous_scale='Greens'
        )
        fig_location.update_layout(height=400, template='plotly_dark')
        st.plotly_chart(fig_location, use_container_width=True)
    
    with col2:
        st.subheader("Home Year Distribution")
        year_data = pd.DataFrame.from_dict(
            group_details['yearHome'],
            orient='index',
            columns=['Count']
        ).sort_values('Count', ascending=False)
        
        fig_year = px.bar(
            year_data,
            y=year_data.index,
            x='Count',
            orientation='h',
            title='Home Age Distribution',
            color='Count',
            color_continuous_scale='Oranges'
        )
        fig_year.update_layout(height=400, template='plotly_dark')
        st.plotly_chart(fig_year, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("Summary Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Apartments", sum(group_details['dwelling type'].values()))
        st.metric("City-Centre/Urban", group_details['placeLocation']['city-centre/urban'])
    
    with col2:
        st.metric("Renters", group_details['dwelling ownership']['renter'])
        st.metric("Home-Owners", group_details['dwelling ownership']['home-owner'])
    
    with col3:
        st.metric("Employees", group_details['socioCat']['employees'])
        st.metric("Knowledge Workers", group_details['socioCat']['executives_knowledge-workers'])

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "<p>⚡ Electricity Apartment Consumption Analysis | Data Period: Oct 2022 - Sep 2023</p>"
    "</div>",
    unsafe_allow_html=True
)
