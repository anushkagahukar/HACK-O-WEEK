# Washington DC Weather Analysis Dashboard

A comprehensive Streamlit application for analyzing Washington DC weather data with interactive visualizations and insights.

## Features

### 📈 Overview
- Quick statistics: Average temperature, humidity, precipitation, wind speed
- Weather conditions distribution
- Interactive charts and visualizations

### 🌡️ Temperature Analysis
- Temperature trends over time
- Temperature distribution histogram
- Actual vs Feels Like temperature comparison
- Statistical metrics (mean, max, min, std deviation)

### 🌧️ Precipitation Analysis
- Total precipitation and rainy days tracking
- Daily precipitation trends
- Precipitation vs Humidity correlation
- Precipitation type distribution (rain, snow, etc.)

### 💨 Wind Analysis
- Wind speed and gust trends
- Wind direction polar plot
- Wind speed vs Temperature correlation
- Statistical wind metrics

### 🔄 Climate Patterns
- Monthly climate statistics
- Temperature distribution by month
- Monthly precipitation totals
- Humidity patterns seasonality
- Seasonal trends and patterns

### 📊 Comparative Analysis
- Feature correlation matrix heatmap
- Pressure vs Temperature relationship
- Humidity vs Visibility correlation
- UV Index vs Temperature analysis
- Complete summary statistics

## Installation

1. **Install Python packages:**
```bash
pip install -r requirements.txt
```

## Usage

1. **Navigate to the project directory:**
```bash
cd "c:\Users\Dell\Downloads\archive (3)"
```

2. **Run the Streamlit app:**
```bash
streamlit run app.py
```

3. **Access the dashboard:**
- Open your browser and go to `http://localhost:8501`
- The dashboard will automatically open in your default browser

## Dashboard Controls

**Sidebar Features:**
- **Analysis Type**: Select from 6 different analysis views
- **Date Range Slider**: Filter data by date range for focused analysis

## Data Source

- **Location**: Washington, DC, USA
- **File**: `dc_weather.csv`
- **Features**: Temperature, humidity, precipitation, wind, pressure, visibility, UV index, and more

## Data Columns

- `datetime`: Date of the weather record
- `temp`: Average temperature (°C)
- `tempmax/tempmin`: Maximum and minimum temperature (°C)
- `humidity`: Humidity percentage (%)
- `precip`: Precipitation (mm)
- `precipprob`: Probability of precipitation (%)
- `windspeed/windgust`: Wind speed and gust (km/h)
- `winddir`: Wind direction (degrees)
- `sealevelpressure`: Sea level pressure (hPa)
- `cloudcover`: Cloud cover percentage (%)
- `visibility`: Visibility (km)
- `uvindex`: UV Index
- `conditions`: Weather condition description

## Key Insights

The dashboard provides insights into:
- Seasonal weather patterns
- Temperature and precipitation correlations
- Wind patterns and their relationship with other variables
- Humidity trends
- Extreme weather events
- Long-term climate trends

## Technologies Used

- **Streamlit**: Interactive web app framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations
- **Matplotlib & Seaborn**: Statistical visualizations
- **NumPy**: Numerical computations

## Tips for Best Use

1. Use the date range slider to focus on specific periods
2. Compare different analysis types to identify patterns
3. Hover over interactive charts for detailed information
4. The correlation matrix helps identify relationships between variables
5. Monthly analysis reveals seasonal patterns

## Performance Notes

- First load may take a few seconds as data is cached
- Interactive elements load smoothly thanks to Streamlit's caching
- Works best with datasets up to several years of daily weather data

---
**Created with Streamlit** | Data Analysis Dashboard for Weather Forecasting & Climate Insights
