# Room Occupancy Detection Analysis Dashboard

A comprehensive Streamlit-based interactive dashboard for analyzing room occupancy detection data with environmental factors like CO₂ concentration, temperature, and humidity.

## Features

### 📊 Time Series Analysis
- Track CO₂ concentration, temperature, and humidity over time
- Color-coded by occupancy status
- Interactive timeline with zoom capabilities

### 📈 Environmental Factors
- Box plots comparing environmental metrics between occupied and unoccupied rooms
- Distribution analysis of CO₂, temperature, and humidity
- Identify patterns in environmental changes

### 🎯 Occupancy Patterns
- Hourly occupancy patterns throughout the day
- Daily occupancy trends (by day of week)
- Heat map visualization of occupancy by hour and day
- Identify peak and off-peak occupancy periods

### 🔗 Correlations
- Correlation matrix of all environmental features
- Scatter plots showing relationships between features and occupancy
- Identify which metrics best predict occupancy

### 📍 Room Analysis
- Per-room occupancy statistics
- Room type comparisons
- Average environmental conditions by room
- Record distribution across rooms

### 🧮 Statistics
- Comprehensive summary statistics
- Data quality metrics
- Occupancy distribution visualization
- Missing value analysis

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. Navigate to the project directory:
```bash
cd "c:\Users\Dell\Downloads\archive (2)"
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Make sure you're in the project directory
2. Run the Streamlit app:
```bash
streamlit run streamlit_app.py
```

3. The app will open in your default web browser (usually at `http://localhost:8501`)

## Data Requirements

The application expects a CSV file named `room_occupancy_detection_data.csv` with the following columns:

- `datetime`: Date and time of the measurement
- `indoor_co2_concentration`: CO₂ level in ppm
- `indoor_operative_temperature`: Temperature in °C
- `indoor_relative_humidity`: Humidity in %
- `occupancy_ground_truth`: Binary indicator (0=unoccupied, 1=occupied)
- `room_number`: Room identifier
- `room_type`: Type of room (e.g., bedroom, kitchen, office)
- `hour_of_the_day`: Hour of measurement (0-23)
- `day_number_of_the_week`: Day of week (0-6, where 0 is Monday)
- Plus additional derived metrics (CO₂ changes, temperature changes, etc.)

## Usage

### Filters (Sidebar)
- **Date Range**: Select specific time period for analysis
- **Room Selection**: Filter by specific rooms
- **Room Type**: Filter by room category
- **Occupancy Status**: View occupied/unoccupied data

### Tabs
1. **Time Series**: View environmental metrics over time
2. **Environmental Factors**: Analyze distributions and comparisons
3. **Occupancy Patterns**: Identify temporal patterns
4. **Correlations**: Explore relationships between variables
5. **Room Analysis**: Compare rooms and room types
6. **Statistics**: View summary statistics and data quality

## Key Insights You Can Extract

- **Peak Occupancy Times**: Identify when rooms are most likely to be occupied
- **Environmental Indicators**: Determine which metrics best indicate occupancy
- **Room Patterns**: Compare occupancy behaviors across different rooms
- **Seasonal/Weekly Patterns**: Understand how occupancy varies by day or time
- **Environmental Comfort**: Analyze temperature and humidity during occupancy

## Requirements

See `requirements.txt` for all dependencies:
- `streamlit`: Web app framework
- `pandas`: Data manipulation
- `numpy`: Numerical computing
- `plotly`: Interactive visualizations

## Troubleshooting

### "Module not found" errors
```bash
pip install --upgrade -r requirements.txt
```

### Port already in use
```bash
streamlit run streamlit_app.py --logger.level=debug --server.port 8502
```

### Slow loading
- Reduce the date range in filters
- Close other applications to free up resources

## Future Enhancements

- Machine learning model for occupancy prediction
- Real-time data monitoring
- Export reports and visualizations
- Anomaly detection
- Energy consumption estimation based on occupancy

## License

This project is open source and available for educational and research purposes.

## Support

For issues or questions, please check the data format and ensure the CSV file is in the same directory as the application.
