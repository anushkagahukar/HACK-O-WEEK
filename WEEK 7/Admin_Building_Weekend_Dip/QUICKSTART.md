# Admin Building Weekend Dip - Quick Start Guide

## 🎯 Get Started in 5 Minutes

This guide will help you set up and run the Admin Building Weekend Dip analysis project.

---

## ✅ Prerequisites

- **Python 3.8 or higher** installed
- **pip** package manager
- A terminal or command prompt
- (Optional) Your own energy consumption CSV data

---

## 🚀 Step-by-Step Setup

### Step 1: Navigate to Project Directory

Open a terminal/PowerShell and navigate to the project folder:

**Windows (PowerShell):**
```powershell
cd "C:\Users\HP\OneDrive\Desktop\WEEK 6\Admin_Building_Weekend_Dip"
```

**Mac/Linux:**
```bash
cd ~/Desktop/WEEK\ 6/Admin_Building_Weekend_Dip
```

### Step 2: Install Dependencies

Install all required packages:

```bash
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed pandas-X.X.X numpy-X.X.X scikit-learn-X.X.X matplotlib-X.X.X seaborn-X.X.X streamlit-X.X.X
```

### Step 3: Generate Sample Data (if needed)

If you don't have your own energy data, generate a sample dataset:

```bash
python generate_sample_data.py
```

**Expected output:**
```
✓ Sample dataset generated successfully!
  Location: data/energy_data.csv
  Shape: (8760, 4)
  Date range: 2023-01-01 to 2023-12-31
```

### Step 4: Choose Your Analysis Method

#### **Option A: Interactive Dashboard (Recommended)**

Perfect for exploring data visually:

```bash
streamlit run dashboard.py
```

The dashboard will automatically open at `http://localhost:8501`

You can:
- Upload your own CSV file
- Adjust clustering and forecast parameters
- View interactive visualizations
- Export insights

#### **Option B: Command-Line Analysis**

For programmatic analysis with automatic report generation:

```bash
python analysis_example.py
```

This will:
- Load the energy data
- Perform K-Means clustering
- Generate polynomial regression forecasts
- Create visualization charts
- Generate CSV reports
- Print detailed console output

#### **Option C: Custom Python Script**

For advanced users who want to write custom code:

```python
from src.data_loader import EnergyDataLoader
from src.clustering import EnergyClusterer
from src.regression import EnergyRegressor

# Load data
loader = EnergyDataLoader()
loader.load_data('data/energy_data.csv')
daily_data = loader.get_daily_data()

# Cluster
clusterer = EnergyClusterer()
clusterer.fit(daily_data, n_clusters=3)

# Forecast
regressor = EnergyRegressor()
regressor.fit(daily_data, degree=2)
regressor.forecast(days_into_future=30)
```

---

## 📊 What to Expect

### Clustering Results:
The algorithm identifies three energy usage patterns:
- **🔴 High Usage**: Peak consumption periods (typically weekdays 9AM-5PM)
- **🟠 Medium Usage**: Moderate consumption periods
- **🟢 Low Usage**: Minimal consumption periods (typically nights and weekends)

### Key Metrics:
- **Weekend Dip**: Percentage reduction from weekday to weekend usage
- **Savings Potential**: How much energy could be saved if weekday usage matched weekend levels
- **R² Score**: How well the regression model fits the data (0-1, higher is better)

### Sample Output:
```
Weekend Dip: 46.20%
Weekday Avg Usage: 65.42 kWh
Weekend Avg Usage: 35.18 kWh
Potential Savings: 30.24 kWh per weekday (46.20%)
```

---

## 📁 Your Data Format

If using your own CSV file, ensure it has these columns:

```csv
Date,Day,Hour,Energy_Consumption
2023-01-01,Sunday,0,18.45
2023-01-01,Sunday,1,16.82
2023-01-02,Monday,0,28.34
```

| Column | Format | Example |
|--------|--------|---------|
| **Date** | YYYY-MM-DD | 2023-01-01 |
| **Day** | Day name | Monday, Sunday |
| **Hour** | Integer 0-23 | 14 |
| **Energy_Consumption** | Number (kWh) | 45.32 |

---

## 🎨 Dashboard Tour

### Main Sections:

1. **Configuration Sidebar** (left)
   - Upload CSV file
   - Select sample data
   - Adjust parameters

2. **Data Summary** (top)
   - Total days analyzed
   - Weekday/Weekend breakdown
   - Average consumption

3. **Clustering Results**
   - Scatter plot with cluster centers
   - Pie chart of cluster distribution
   - Cluster statistics table

4. **Weekday vs Weekend**
   - Side-by-side bar chart
   - Weekend dip percentage
   - Immediate savings potential

5. **Forecasting**
   - Line charts showing historical + forecast
   - Model performance metrics
   - Trend indicators

6. **Savings Analysis**
   - Detailed savings potential
   - Target usage levels
   - Percentage breakdowns

7. **Data Tables**
   - View raw daily/hourly data
   - Cluster assignments
   - Export capability

---

## 🧪 Test the Installation

Run this quick verification:

```bash
python -c "import pandas; import sklearn; import streamlit; print('✓ All packages installed!')"
```

If successful, you'll see:
```
✓ All packages installed!
```

---

## 📋 Common Tasks

### Upload Your Own Data

1. Click "📁 Upload Energy Data (CSV)" in the sidebar
2. Select your CSV file
3. Dashboard automatically updates with your data

### Change Clustering Parameters

1. Adjust "Number of Clusters" slider in sidebar (2-5)
2. Click the reload button or change another parameter
3. Clustering automatically recalculates

### Extend Forecast Period

1. Move "Forecast Days" slider in sidebar (7-90)
2. Dashboard updates with longer forecasts
3. View extended predictions

### Export Analysis Results

From the analysis_example.py script:
- `output_daily_summary.csv` - Detailed daily statistics
- `output_cluster_visualization.png` - Clustering scatter plot
- `output_forecast_visualization.png` - Forecast charts
- `output_comprehensive_dashboard.png` - All metrics in one image

---

## 🔧 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'streamlit'"

**Solution**: Reinstall requirements:
```bash
pip install --upgrade -r requirements.txt
```

### Problem: "FileNotFoundError: data/energy_data.csv"

**Solution**: Generate sample data:
```bash
python generate_sample_data.csv
```

### Problem: "Port 8501 already in use"

**Solution**: Run on different port:
```bash
streamlit run dashboard.py --server.port 8502
```

### Problem: Slow performance on large dataset

**Solution**: 
- Reduce the date range in your CSV
- Use fewer clusters (2 instead of 3)
- Lower polynomial degree (1 instead of 2)

### Problem: "Permission denied" error

**Solution** (Windows):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📚 Project Structure

```
Admin_Building_Weekend_Dip/
├── src/                    # Core modules
│   ├── data_loader.py     # Load and preprocess data
│   ├── clustering.py      # K-Means clustering
│   ├── regression.py      # Forecasting models
│   └── utils.py           # Helper functions
├── data/                   # Data directory
│   └── energy_data.csv    # Sample dataset
├── dashboard.py           # Streamlit dashboard
├── analysis_example.py    # Standalone analysis script
├── generate_sample_data.py # Generate sample data
├── requirements.txt       # Package dependencies
├── README.md              # Detailed documentation
└── QUICKSTART.md          # This file
```

---

## 💡 Tips & Tricks

### 1. **Compare Different Forecasts**
   - Change polynomial degree in sidebar
   - Compare R² scores to find best fit

### 2. **Identify Peak Hours**
   - Look at hourly data in Dashboard tab
   - Focus efficiency efforts on peak times

### 3. **Weekend Patterns**
   - Filter by "Weekend" in day type
   - Understand what drives weekend consumption
   - Set realistic reduction targets

### 4. **Seasonal Trends**
   - Check if consumption increases over time
   - Use forecasts to plan maintenance
   - Adjust AC/heating based on predictions

### 5. **Cluster Insights**
   - Low cluster: Baseline essential consumption
   - Medium cluster: Normal operations
   - High cluster: Peak demand periods

---

## 🎓 Learning Outcomes

By using this project, you'll understand:

✅ **K-Means Clustering**: How to identify patterns in energy data  
✅ **Polynomial Regression**: How to forecast future consumption  
✅ **Feature Engineering**: Preparing time-series data for analysis  
✅ **Data Visualization**: Creating insights from complex data  
✅ **Savings Analysis**: Quantifying energy efficiency opportunities  

---

## 🚀 Next Steps

1. **Explore the Dashboard**: Spend 10 minutes clicking around
2. **Upload Your Data**: Try with real building data
3. **Adjust Parameters**: See how clustering/forecasting changes
4. **Generate Reports**: Use analysis_example.py for automation
5. **Customize**: Modify code for your specific needs

---

## 📞 Support Resources

- **README.md**: Comprehensive documentation
- **Code Comments**: Detailed explanations in each module
- **Example Script**: analysis_example.py shows all features
- **Dashboard Help**: Hover over labels for explanations

---

## ⏱️ Typical Workflow

### Time Required:
- **Setup**: 5 minutes
- **First Analysis**: 2 minutes (sample data)
- **Custom Data**: 10 minutes (upload + explore)
- **Deep Dive**: 30+ minutes (adjust parameters, extract insights)

### Typical Session:
1. **Load Data** (1 min)
2. **Explore Clusters** (3 min)
3. **Review Forecasts** (2 min)
4. **Check Savings** (1 min)
5. **Export Results** (1 min)

---

## 🎉 You're Ready!

Everything is set up. Choose your preferred method above and start analyzing!

**Recommended First Step:**
```bash
streamlit run dashboard.py
```

Then explore the interactive dashboard with sample data.

---

**Happy analyzing! 📊⚡**

Last Updated: February 2024
