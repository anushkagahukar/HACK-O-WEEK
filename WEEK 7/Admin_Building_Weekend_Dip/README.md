# Admin Building Weekend Dip Analysis

A comprehensive Python-based project for analyzing building energy consumption patterns, detecting weekend dips, forecasting future usage, and calculating savings potential.

## 📋 Project Overview

This project analyzes energy consumption data to:
- **Detect Patterns**: Identify High, Medium, and Low usage clusters using K-Means clustering
- **Forecast Usage**: Predict future energy consumption using polynomial regression
- **Quantify Savings**: Calculate potential energy savings on weekends and during off-peak hours
- **Visualize Data**: Create interactive dashboards and comprehensive reports

## 🏗️ Project Structure

```
Admin_Building_Weekend_Dip/
├── data/
│   └── energy_data.csv              # Sample dataset (auto-generated)
├── src/
│   ├── __init__.py                  # Package initialization
│   ├── data_loader.py               # Load and preprocess CSV data
│   ├── clustering.py                # K-Means clustering implementation
│   ├── regression.py                # Polynomial regression & forecasting
│   └── utils.py                     # Utility functions
├── dashboard.py                     # Streamlit interactive dashboard
├── generate_sample_data.py           # Generate sample dataset
├── requirements.txt                 # Project dependencies
├── README.md                        # This file
└── analysis_example.py              # Example analysis script
```

## 🚀 Quick Start

### 1. **Install Dependencies**

```bash
pip install -r requirements.txt
```

### 2. **Generate Sample Data (Optional)**

If you don't have your own energy data:

```bash
python generate_sample_data.py
```

This creates `data/energy_data.csv` with 365 days of realistic energy consumption patterns.

### 3. **Launch the Interactive Dashboard**

```bash
streamlit run dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

### 4. **Run Analysis Script (Advanced)**

For programmatic analysis with custom parameters:

```bash
python analysis_example.py
```

## 📊 Dashboard Features

### 🎯 Main Sections:

1. **Data Summary Metrics**
   - Total days analyzed
   - Weekday/Weekend split
   - Average hourly consumption

2. **Clustering Analysis**
   - K-Means clustering result visualization
   - Cluster distribution pie chart
   - High, Medium, and Low usage profiles

3. **Weekday vs Weekend Comparison**
   - Side-by-side consumption comparison
   - Weekend dip percentage
   - Immediate savings potential

4. **Energy Forecasting**
   - Polynomial regression models for each cluster
   - 30-day forward forecast visualization
   - Model performance metrics (R², RMSE, MAE)

5. **Savings Potential**
   - Detailed savings analysis
   - Target vs current usage comparison
   - Percentage and absolute savings metrics

6. **Data Views**
   - Daily summary statistics
   - Detailed daily data with cluster assignments
   - Hourly energy consumption records

## 📈 Data Format

Your CSV file should contain:

| Column | Type | Description |
|--------|------|-------------|
| Date | YYYY-MM-DD | Calendar date |
| Day | String | Day of week (Monday, Tuesday, etc.) |
| Hour | 0-23 | Hour of day |
| Energy_Consumption | Float | Energy in kWh |

### Example:
```csv
Date,Day,Hour,Energy_Consumption
2023-01-01,Sunday,0,18.45
2023-01-01,Sunday,1,16.82
2023-01-02,Monday,0,28.34
2023-01-02,Monday,1,29.12
```

## 🔧 Core Modules

### `data_loader.py`
- **EnergyDataLoader**: Main class for loading and preprocessing data
- Calculates daily statistics (total, average, min, max consumption)
- Classifies days as weekday or weekend
- Provides summary statistics

```python
from src.data_loader import EnergyDataLoader

loader = EnergyDataLoader()
loader.load_data('data/energy_data.csv')
hourly_data = loader.get_hourly_data()
daily_data = loader.get_daily_data()
```

### `clustering.py`
- **EnergyClusterer**: K-Means clustering implementation
- Identifies three usage patterns: Low, Medium, High
- Visualizes clusters with scatter plots
- Provides cluster statistics and characterization

```python
from src.clustering import EnergyClusterer

clusterer = EnergyClusterer()
clusterer.fit(daily_data, n_clusters=3)
clusterer.visualize_clusters()
cluster_info = clusterer.get_cluster_info()
```

### `regression.py`
- **EnergyRegressor**: Polynomial regression for forecasting
- Fits separate models for each cluster
- Generates 30-day forecasts
- Provides performance metrics (R², RMSE, MAE)

```python
from src.regression import EnergyRegressor

regressor = EnergyRegressor()
regressor.fit(daily_data, degree=2)
regressor.forecast(days_into_future=30)
regressor.visualize_forecasts(daily_data)
```

### `utils.py`
- **Utility Functions**:
  - `classify_weekday_weekend()`: Classify days
  - `calculate_daily_stats()`: Aggregate hourly to daily data
  - `calculate_savings_potential()`: Quantify savings opportunities
  - `normalize_features()`: Feature scaling helpers
  - `print_metrics()`: Pretty-print analysis results

```python
from src.utils import calculate_savings_potential

metrics = calculate_savings_potential(weekday_avg=65.5, weekend_avg=35.2)
print_metrics(metrics)
```

## 🎓 Understanding the Analysis

### K-Means Clustering
The algorithm identifies three distinct energy usage patterns:
- **High Usage**: Days with peak consumption (typically weekdays during business hours)
- **Medium Usage**: Days with moderate consumption
- **Low Usage**: Days with minimal consumption (typically weekends)

### Polynomial Regression
Forecasts future consumption using polynomial features:
- **Degree 1**: Linear trend (simplest)
- **Degree 2**: Quadratic curve (recommended)
- **Degree 3**: Cubic curve (complex patterns)

### Savings Potential
Calculated as the difference between:
- **Current Usage**: Actual weekday/weekend consumption
- **Target Usage**: Weekend consumption (most efficient baseline)

## 📊 Sample Output

### Clustering Results:
```
Cluster Distribution:
  Low      (Cluster 0) - 104 days (28.5%)
  Medium   (Cluster 1) - 156 days (42.7%)
  High     (Cluster 2) -  105 days (28.8%)
```

### Forecast Summary:
```
Low Cluster:
  Mean Forecasted Usage: 32.45 kWh
  Trend: stable
  R² Score: 0.8234

Medium Cluster:
  Mean Forecasted Usage: 48.92 kWh
  Trend: decreasing
  R² Score: 0.7891
```

### Savings Analysis:
```
ENERGY SAVINGS ANALYSIS
Weekday Average Usage:        65.42 kWh
Weekend Average Usage:        35.18 kWh
Target Usage Level:           35.18 kWh
Weekend Dip:                  46.20%
Weekday Savings Potential:    30.24 kWh (46.20%)
```

## ⚙️ Configuration Options

In the Streamlit dashboard sidebar:

1. **File Upload**: Select your energy data CSV
2. **Number of Clusters**: 2-5 clusters for K-Means (default: 3)
3. **Polynomial Degree**: 1-3 for regression (default: 2)
4. **Forecast Days**: 7-90 days ahead (default: 30)

## 🔍 Advanced Usage

### Custom Analysis Script
Create a Python script for automation:

```python
from src.data_loader import EnergyDataLoader
from src.clustering import EnergyClusterer
from src.regression import EnergyRegressor
from src.utils import calculate_savings_potential

# Load data
loader = EnergyDataLoader()
loader.load_data('data/energy_data.csv')
daily_data = loader.get_daily_data()
loader.print_summary()

# Clustering
clusterer = EnergyClusterer()
clusterer.fit(daily_data, n_clusters=3)
clusterer.print_cluster_summary()

# Regression
regressor = EnergyRegressor()
regressor.fit(daily_data, degree=2)
regressor.forecast(days_into_future=30)
regressor.print_forecast_summary()

# Savings analysis
weekday_data = daily_data[daily_data['Day_Type'] == 'Weekday']
weekend_data = daily_data[daily_data['Day_Type'] == 'Weekend']
metrics = calculate_savings_potential(
    weekday_data['Daily_Avg'].mean(),
    weekend_data['Daily_Avg'].mean()
)
print_metrics(metrics)
```

## 📋 Requirements

- **Python 3.8+**
- **pandas**: Data manipulation
- **numpy**: Numerical computing
- **scikit-learn**: Machine learning (K-Means, regression)
- **matplotlib & seaborn**: Visualization
- **streamlit**: Interactive dashboard

## 🐛 Troubleshooting

### Issue: "Module not found" errors
**Solution**: Ensure you're running from the project root directory and have installed all requirements:
```bash
pip install -r requirements.txt
```

### Issue: "No data loaded"
**Solution**: 
- Generate sample data: `python generate_sample_data.py`
- Or upload your CSV file in the dashboard

### Issue: Streamlit port already in use
**Solution**: Run on a different port:
```bash
streamlit run dashboard.py --server.port 8502
```

## 📝 Comments & Code Quality

All code includes:
- ✅ Comprehensive docstrings
- ✅ Type hints
- ✅ Inline comments explaining logic
- ✅ Error handling and validation
- ✅ Professional structure and naming

## 🎯 Use Cases

This project is ideal for:
- 🏢 Facilities management teams
- ⚡ Energy consultants
- 📊 Building operators
- 🔬 Energy researchers
- 💼 Sustainability managers

## 📄 License

This project is provided as-is for educational and analytical purposes.

## 🤝 Contributing

To extend this project:
1. Add new clustering algorithms (DBSCAN, Gaussian Mixture Models)
2. Implement additional regression models (Random Forest, Neural Networks)
3. Add weather data integration for improved forecasting
4. Create automated reporting features
5. Add anomaly detection for unusual consumption patterns

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review code comments and docstrings
3. Examine example analysis scripts
4. Validate data format against the expected CSV schema

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Status**: Production Ready ✅
