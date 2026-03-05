import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Room Occupancy Detection Analysis",
    page_icon="📊",
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
    .title-section {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('room_occupancy_detection_data.csv')
    df['datetime'] = pd.to_datetime(df['datetime'], format='%d-%m-%y %H:%M')
    return df

df = load_data()

# Title
st.markdown("""
    <div class="title-section">
        <h1>🏠 Room Occupancy Detection Analysis</h1>
        <p>Comprehensive Environmental and Occupancy Data Exploration</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar filters
with st.sidebar:
    st.header("🔧 Filters & Settings")
    
    # Date range filter
    min_date = df['datetime'].min()
    max_date = df['datetime'].max()
    date_range = st.date_input(
        "Select Date Range",
        value=(min_date.date(), max_date.date()),
        min_value=min_date.date(),
        max_value=max_date.date()
    )
    
    # Room filter
    unique_rooms = sorted(df['room_number'].unique())
    selected_rooms = st.multiselect(
        "Select Rooms",
        unique_rooms,
        default=unique_rooms
    )
    
    # Room type filter
    room_types = sorted(df['room_type'].dropna().unique())
    selected_room_types = st.multiselect(
        "Select Room Types",
        room_types,
        default=room_types
    )
    
    # Occupancy filter
    occupancy_filter = st.multiselect(
        "Occupancy Status",
        [0, 1],
        default=[0, 1],
        format_func=lambda x: "Occupied" if x == 1 else "Unoccupied"
    )

# Filter data based on selections
filtered_df = df[
    (df['datetime'].dt.date >= date_range[0]) &
    (df['datetime'].dt.date <= date_range[1]) &
    (df['room_number'].isin(selected_rooms)) &
    (df['room_type'].isin(selected_room_types)) &
    (df['occupancy_ground_truth'].isin(occupancy_filter))
].copy()

# Display key statistics
st.header("📈 Key Statistics")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total Records",
        f"{len(filtered_df):,}",
        f"{len(filtered_df)/len(df)*100:.1f}% of data"
    )

with col2:
    occupancy_rate = (filtered_df['occupancy_ground_truth'].sum() / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
    st.metric(
        "Occupancy Rate",
        f"{occupancy_rate:.1f}%",
        f"{filtered_df['occupancy_ground_truth'].sum():.0f} occupied records"
    )

with col3:
    avg_co2 = filtered_df['indoor_co2_concentration'].mean()
    st.metric(
        "Avg CO₂ (ppm)",
        f"{avg_co2:.1f}",
        f"Range: {filtered_df['indoor_co2_concentration'].min():.0f}-{filtered_df['indoor_co2_concentration'].max():.0f}"
    )

with col4:
    avg_temp = filtered_df['indoor_operative_temperature'].mean()
    st.metric(
        "Avg Temperature (°C)",
        f"{avg_temp:.1f}",
        f"Range: {filtered_df['indoor_operative_temperature'].min():.1f}-{filtered_df['indoor_operative_temperature'].max():.1f}"
    )

with col5:
    avg_humidity = filtered_df['indoor_relative_humidity'].mean()
    st.metric(
        "Avg Humidity (%)",
        f"{avg_humidity:.1f}",
        f"Range: {filtered_df['indoor_relative_humidity'].min():.1f}-{filtered_df['indoor_relative_humidity'].max():.1f}"
    )

# Tabs for different analyses
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Time Series", 
    "📈 Environmental Factors", 
    "🎯 Occupancy Patterns",
    "🔗 Correlations",
    "📍 Room Analysis",
    "🧮 Statistics"
])

# Tab 1: Time Series Analysis
with tab1:
    st.subheader("Time Series Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CO2 over time
        fig_co2 = px.line(
            filtered_df.sort_values('datetime'),
            x='datetime',
            y='indoor_co2_concentration',
            color='occupancy_ground_truth',
            title='CO₂ Concentration Over Time',
            labels={'indoor_co2_concentration': 'CO₂ (ppm)', 'datetime': 'Date Time', 'occupancy_ground_truth': 'Occupied'},
            color_discrete_map={0: '#FF6B6B', 1: '#4ECDC4'}
        )
        fig_co2.update_xaxes(rangeslider_visible=False)
        st.plotly_chart(fig_co2, use_container_width=True)
    
    with col2:
        # Temperature over time
        fig_temp = px.line(
            filtered_df.sort_values('datetime'),
            x='datetime',
            y='indoor_operative_temperature',
            color='occupancy_ground_truth',
            title='Temperature Over Time',
            labels={'indoor_operative_temperature': 'Temperature (°C)', 'datetime': 'Date Time', 'occupancy_ground_truth': 'Occupied'},
            color_discrete_map={0: '#FF6B6B', 1: '#4ECDC4'}
        )
        fig_temp.update_xaxes(rangeslider_visible=False)
        st.plotly_chart(fig_temp, use_container_width=True)
    
    # Humidity over time
    fig_humidity = px.line(
        filtered_df.sort_values('datetime'),
        x='datetime',
        y='indoor_relative_humidity',
        color='occupancy_ground_truth',
        title='Humidity Over Time',
        labels={'indoor_relative_humidity': 'Humidity (%)', 'datetime': 'Date Time', 'occupancy_ground_truth': 'Occupied'},
        color_discrete_map={0: '#FF6B6B', 1: '#4ECDC4'}
    )
    fig_humidity.update_xaxes(rangeslider_visible=False)
    st.plotly_chart(fig_humidity, use_container_width=True)

# Tab 2: Environmental Factors
with tab2:
    st.subheader("Environmental Factors Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CO2 distribution
        fig_co2_dist = px.box(
            filtered_df,
            y='indoor_co2_concentration',
            x='occupancy_ground_truth',
            title='CO₂ Distribution by Occupancy',
            labels={'indoor_co2_concentration': 'CO₂ (ppm)', 'occupancy_ground_truth': 'Occupied'},
            color='occupancy_ground_truth',
            color_discrete_map={0: '#FF6B6B', 1: '#4ECDC4'}
        )
        fig_co2_dist.update_xaxes(ticktext=['Unoccupied', 'Occupied'], tickvals=[0, 1])
        st.plotly_chart(fig_co2_dist, use_container_width=True)
    
    with col2:
        # Temperature distribution
        fig_temp_dist = px.box(
            filtered_df,
            y='indoor_operative_temperature',
            x='occupancy_ground_truth',
            title='Temperature Distribution by Occupancy',
            labels={'indoor_operative_temperature': 'Temperature (°C)', 'occupancy_ground_truth': 'Occupied'},
            color='occupancy_ground_truth',
            color_discrete_map={0: '#FF6B6B', 1: '#4ECDC4'}
        )
        fig_temp_dist.update_xaxes(ticktext=['Unoccupied', 'Occupied'], tickvals=[0, 1])
        st.plotly_chart(fig_temp_dist, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Humidity distribution
        fig_humidity_dist = px.box(
            filtered_df,
            y='indoor_relative_humidity',
            x='occupancy_ground_truth',
            title='Humidity Distribution by Occupancy',
            labels={'indoor_relative_humidity': 'Humidity (%)', 'occupancy_ground_truth': 'Occupied'},
            color='occupancy_ground_truth',
            color_discrete_map={0: '#FF6B6B', 1: '#4ECDC4'}
        )
        fig_humidity_dist.update_xaxes(ticktext=['Unoccupied', 'Occupied'], tickvals=[0, 1])
        st.plotly_chart(fig_humidity_dist, use_container_width=True)
    
    with col2:
        # CO2 change distribution
        fig_co2_change = px.box(
            filtered_df,
            y='current_value_minus_average_last_hour_co2',
            x='occupancy_ground_truth',
            title='CO₂ Change (Last Hour) by Occupancy',
            labels={'current_value_minus_average_last_hour_co2': 'CO₂ Change (ppm)', 'occupancy_ground_truth': 'Occupied'},
            color='occupancy_ground_truth',
            color_discrete_map={0: '#FF6B6B', 1: '#4ECDC4'}
        )
        fig_co2_change.update_xaxes(ticktext=['Unoccupied', 'Occupied'], tickvals=[0, 1])
        st.plotly_chart(fig_co2_change, use_container_width=True)

# Tab 3: Occupancy Patterns
with tab3:
    st.subheader("Occupancy Patterns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Occupancy by hour
        hourly_occupancy = filtered_df.groupby('hour_of_the_day')['occupancy_ground_truth'].agg(['sum', 'count'])
        hourly_occupancy['occupancy_rate'] = (hourly_occupancy['sum'] / hourly_occupancy['count'] * 100)
        
        fig_hourly = px.bar(
            hourly_occupancy.reset_index(),
            x='hour_of_the_day',
            y='occupancy_rate',
            title='Occupancy Rate by Hour of Day',
            labels={'hour_of_the_day': 'Hour of Day', 'occupancy_rate': 'Occupancy Rate (%)'},
            color='occupancy_rate',
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig_hourly, use_container_width=True)
    
    with col2:
        # Occupancy by day of week
        day_labels = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
        daily_occupancy = filtered_df.groupby('day_number_of_the_week')['occupancy_ground_truth'].agg(['sum', 'count'])
        daily_occupancy['occupancy_rate'] = (daily_occupancy['sum'] / daily_occupancy['count'] * 100)
        daily_occupancy['day_name'] = daily_occupancy.index.map(day_labels)
        
        fig_daily = px.bar(
            daily_occupancy.reset_index(),
            x='day_name',
            y='occupancy_rate',
            title='Occupancy Rate by Day of Week',
            labels={'day_name': 'Day of Week', 'occupancy_rate': 'Occupancy Rate (%)'},
            color='occupancy_rate',
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig_daily, use_container_width=True)
    
    # Heatmap: Hour vs Day
    pivot_occupancy = filtered_df.pivot_table(
        values='occupancy_ground_truth',
        index='hour_of_the_day',
        columns='day_number_of_the_week',
        aggfunc='mean'
    )
    # Map day numbers to names, handling missing days
    day_labels_mapping = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
    pivot_occupancy.columns = [day_labels_mapping.get(int(col), str(col)) for col in pivot_occupancy.columns]
    
    fig_heatmap = px.imshow(
        pivot_occupancy * 100,
        title='Occupancy Heatmap: Hour vs Day of Week',
        labels={'x': 'Day of Week', 'y': 'Hour of Day', 'color': 'Occupancy (%)'},
        color_continuous_scale='YlOrRd'
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

# Tab 4: Correlations
with tab4:
    st.subheader("Correlation Analysis")
    
    # Select features for correlation
    features = [
        'indoor_co2_concentration',
        'indoor_operative_temperature',
        'indoor_relative_humidity',
        'current_value_minus_average_last_hour_co2',
        'current_value_minus_average_last_hour_operative_temperature',
        'current_value_minus_average_last_hour_relative_humidity',
        'occupancy_ground_truth'
    ]
    
    corr_matrix = filtered_df[features].corr()
    
    fig_corr = px.imshow(
        corr_matrix,
        title='Correlation Matrix of Environmental Features',
        color_continuous_scale='RdBu',
        zmin=-1,
        zmax=1,
        aspect='auto'
    )
    st.plotly_chart(fig_corr, use_container_width=True)
    
    # Feature vs Occupancy scatter plots
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fig_co2_scatter = px.scatter(
            filtered_df.sample(min(500, len(filtered_df))),
            x='indoor_co2_concentration',
            y='occupancy_ground_truth',
            title='CO₂ vs Occupancy',
            color='occupancy_ground_truth',
            color_discrete_map={0: '#FF6B6B', 1: '#4ECDC4'},
            labels={'occupancy_ground_truth': 'Occupied'}
        )
        st.plotly_chart(fig_co2_scatter, use_container_width=True)
    
    with col2:
        fig_temp_scatter = px.scatter(
            filtered_df.sample(min(500, len(filtered_df))),
            x='indoor_operative_temperature',
            y='occupancy_ground_truth',
            title='Temperature vs Occupancy',
            color='occupancy_ground_truth',
            color_discrete_map={0: '#FF6B6B', 1: '#4ECDC4'},
            labels={'occupancy_ground_truth': 'Occupied'}
        )
        st.plotly_chart(fig_temp_scatter, use_container_width=True)
    
    with col3:
        fig_humidity_scatter = px.scatter(
            filtered_df.sample(min(500, len(filtered_df))),
            x='indoor_relative_humidity',
            y='occupancy_ground_truth',
            title='Humidity vs Occupancy',
            color='occupancy_ground_truth',
            color_discrete_map={0: '#FF6B6B', 1: '#4ECDC4'},
            labels={'occupancy_ground_truth': 'Occupied'}
        )
        st.plotly_chart(fig_humidity_scatter, use_container_width=True)

# Tab 5: Room Analysis
with tab5:
    st.subheader("Room-wise Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Room statistics
        room_stats = filtered_df.groupby('room_number').agg({
            'occupancy_ground_truth': ['sum', 'count'],
            'indoor_co2_concentration': 'mean',
            'indoor_operative_temperature': 'mean',
            'indoor_relative_humidity': 'mean'
        }).round(2)
        room_stats.columns = ['Occupied Records', 'Total Records', 'Avg CO₂', 'Avg Temp', 'Avg Humidity']
        room_stats['Occupancy Rate (%)'] = (room_stats['Occupied Records'] / room_stats['Total Records'] * 100).round(1)
        
        st.dataframe(room_stats, use_container_width=True)
    
    with col2:
        # Room occupancy comparison
        room_occupancy = filtered_df.groupby('room_number')['occupancy_ground_truth'].agg(['sum', 'count'])
        room_occupancy['occupancy_rate'] = (room_occupancy['sum'] / room_occupancy['count'] * 100)
        
        fig_room_occ = px.bar(
            room_occupancy.reset_index(),
            x='room_number',
            y='occupancy_rate',
            title='Occupancy Rate by Room',
            labels={'room_number': 'Room Number', 'occupancy_rate': 'Occupancy Rate (%)'},
            color='occupancy_rate',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_room_occ, use_container_width=True)
    
    # Room type analysis
    room_type_stats = filtered_df.groupby('room_type').agg({
        'occupancy_ground_truth': ['sum', 'count'],
        'indoor_co2_concentration': 'mean',
        'indoor_operative_temperature': 'mean',
        'indoor_relative_humidity': 'mean'
    }).round(2)
    room_type_stats.columns = ['Occupied Records', 'Total Records', 'Avg CO₂', 'Avg Temp', 'Avg Humidity']
    room_type_stats['Occupancy Rate (%)'] = (room_type_stats['Occupied Records'] / room_type_stats['Total Records'] * 100).round(1)
    
    st.subheader("Room Type Statistics")
    st.dataframe(room_type_stats, use_container_width=True)

# Tab 6: Statistics
with tab6:
    st.subheader("Detailed Statistics")
    
    # Summary statistics
    st.write("### Summary Statistics for Filtered Data")
    
    summary_stats = filtered_df[[
        'indoor_co2_concentration',
        'indoor_operative_temperature',
        'indoor_relative_humidity',
        'current_value_minus_average_last_hour_co2',
        'current_value_minus_average_last_hour_operative_temperature',
        'current_value_minus_average_last_hour_relative_humidity'
    ]].describe().round(2)
    
    st.dataframe(summary_stats, use_container_width=True)
    
    # Occupancy distribution pie chart
    col1, col2 = st.columns(2)
    
    with col1:
        occupancy_counts = filtered_df['occupancy_ground_truth'].value_counts()
        fig_pie = px.pie(
            values=occupancy_counts.values,
            names=['Unoccupied', 'Occupied'],
            title='Occupancy Distribution',
            color_discrete_map={0: '#FF6B6B', 1: '#4ECDC4'},
            hole=0.3
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Room distribution
        room_counts = filtered_df['room_number'].value_counts().sort_index()
        fig_room_dist = px.bar(
            x=room_counts.index,
            y=room_counts.values,
            title='Record Distribution by Room',
            labels={'x': 'Room Number', 'y': 'Number of Records'},
            color=room_counts.values,
            color_continuous_scale='Teal'
        )
        st.plotly_chart(fig_room_dist, use_container_width=True)
    
    # Data quality info
    st.write("### Data Quality Information")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Rows", f"{len(filtered_df):,}")
    with col2:
        missing_pct = (filtered_df.isnull().sum().sum() / (len(filtered_df) * len(filtered_df.columns)) * 100)
        st.metric("Missing Values", f"{missing_pct:.2f}%")
    with col3:
        st.metric("Date Range", f"{filtered_df['datetime'].min().date()} to {filtered_df['datetime'].max().date()}")

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #888; font-size: 12px; padding: 20px;">
        <p>Room Occupancy Detection Analysis Dashboard | Data-driven insights for environmental monitoring</p>
        <p>Built with Streamlit & Plotly</p>
    </div>
""", unsafe_allow_html=True)
