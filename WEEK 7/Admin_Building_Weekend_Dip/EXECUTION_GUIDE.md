PS C:\Users\HP\OneDrive\Desktop\WEEK 7> pip install -r requirements.txt
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "C:\Python313\Scripts\pip.exe\__main__.py", line 6, in <module>
    sys.exit(main())
             ~~~~^^
  File "C:\Python313\Lib\site-packages\pip\_internal\cli\main.py", line 78, in main
    command = create_command(cmd_name, isolated=("--isolated" in cmd_args))
  File "C:\Python313\Lib\site-packages\pip\_internal\commands\__init__.py", line 121, in create_command
    module = importlib.import_module(module_path)
  File "C:\Python313\Lib\importlib\__init__.py", line 88, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 1026, in exec_module
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "C:\Python313\Lib\site-packages\pip\_internal\commands\install.py", line 22, in <module>
    import pip._internal.self_outdated_check  # noqa: F401
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Python313\Lib\site-packages\pip\_internal\self_outdated_check.py", line 20, in <module>
    from pip._internal.index.collector import LinkCollector
  File "C:\Python313\Lib\site-packages\pip\_internal\index\collector.py", line 32, in <module>
    from pip._internal.models.search_scope import SearchScope
  File "C:\Python313\Lib\site-packages\pip\_internal\models\search_scope.py", line 17, in <module>
    @dataclass(frozen=True)
     ~~~~~~~~~^^^^^^^^^^^^^
  File "C:\Python313\Lib\dataclasses.py", line 1295, in wrap
    return _process_class(cls, init, repr, eq, order, unsafe_hash,
                          frozen, match_args, kw_only, slots,
                          weakref_slot)
  File "C:\Python313\Lib\dataclasses.py", line 1157, in _process_class
    func_builder.add_fns_to_class(cls)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^
  File "C:\Python313\Lib\dataclasses.py", line 498, in add_fns_to_class
    exec(txt, self.globals, ns)
    ~~~~^^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 0, in <module>
KeyboardInterrupt
PS C:\Users\HP\OneDrive\Desktop\WEEK 7> python generate_sample_data.py
C:\Python313\python.exe: can't open file 'C:\\Users\\HP\\OneDrive\\Desktop\\WEEK 7\\generate_sample_data.py': [Errno 2] No such file or directory
PS C:\Users\HP\OneDrive\Desktop\WEEK 7> # Admin Building Weekend Dip - Complete Execution Guide

## 📋 Project Summary

**Project Name**: Admin Building Weekend Dip Analysis  
**Version**: 1.0.0  
**Status**: ✅ Ready to Run  
**Date**: February 2024

---

## 🏗️ Project Structure

```
Admin_Building_Weekend_Dip/
│
├── 📁 src/ (Core Modules)
│   ├── __init__.py              # Package initialization
│   ├── data_loader.py           # CSV loader & preprocessor
│   ├── clustering.py            # K-Means clustering (High/Med/Low usage)
│   ├── regression.py            # Polynomial regression & forecasting
│   └── utils.py                 # Helper functions for analysis
│
├── 📁 data/ (Data Directory)
│   └── energy_data.csv          # Sample dataset (auto-generated)
│
├── 📄 Main Scripts
│   ├── dashboard.py             # Streamlit interactive dashboard
│   ├── analysis_example.py      # Standalone analysis with reports
│   └── generate_sample_data.py  # Generate sample dataset
│
├── 📚 Documentation
│   ├── README.md                # Comprehensive documentation
│   ├── QUICKSTART.md            # 5-minute setup guide
│   └── EXECUTION_GUIDE.md       # This file
│
└── 📦 Configuration
    └── requirements.txt         # Python dependencies
```

---

## 🔧 Installation & Setup

### 1. **Install Python Packages**

```bash
pip install -r requirements.txt
```

**Packages installed:**
- pandas (data manipulation)
- numpy (numerical computing)
- scikit-learn (ML algorithms)
- matplotlib (visualization)
- seaborn (advanced plotting)
- streamlit (interactive dashboard)

### 2. **Verify Installation**

```bash
python -c "import pandas, sklearn, streamlit; print('✓ All packages ready!')"
```

### 3. **Generate Sample Data (Optional)**

```bash
python generate_sample_data.py
```

Creates `data/energy_data.csv` with 365 days of realistic energy data.

---

## 🎯 Execution Methods

### **Method 1: Interactive Streamlit Dashboard** ⭐ RECOMMENDED

Best for: Exploring data visually, adjusting parameters, generating insights

```bash
streamlit run dashboard.py
```

**What opens:**
- Interactive web dashboard at `http://localhost:8501`
- Real-time visualizations
- Parameter sliders for customization
- File upload capability
- Export-ready charts

**Features:**
```
✅ 4 Key Metrics (Days, Weekdays, Weekends, Avg Usage)
✅ K-Means Clustering visualization (scatter + pie chart)
✅ Weekday vs Weekend comparison (metrics + bar chart)
✅ Energy forecasting (30-day predictions)
✅ Detailed savings analysis
✅ Data viewports (daily, hourly, cluster details)
```

**Example Workflow:**
1. Open dashboard in browser
2. Use sample data or upload your CSV
3. Adjust clustering parameters (2-5 clusters)
4. Change forecast polynomial degree (1-3)
5. Review all visualizations
6. Extract insights

---

### **Method 2: Programmatic Analysis Script**

Best for: Automated analysis, batch processing, report generation

```bash
python analysis_example.py
```

**What it does:**
1. Loads energy data automatically
2. Performs K-Means clustering
3. Generates polynomial regression models
4. Creates 30-day forecasts
5. Calculates savings potential
6. Generates multiple visualizations
7. Creates summary CSV reports
8. Prints detailed console output

**Generated Files:**
```
✅ output_cluster_visualization.png          (cluster scatter plot)
✅ output_forecast_visualization.png         (historical + forecast)
✅ output_comprehensive_dashboard.png        (6-chart summary)
✅ output_daily_summary.csv                  (detailed daily data)
```

**Console Output Example:**
```
ADMIN BUILDING WEEKEND DIP - COMPREHENSIVE ANALYSIS
======================================================================

STEP 1: Loading and Preprocessing Data
------
✓ Data loaded successfully!
  Records: 8760 hourly entries
  Days: 365 days
  Date range: 2023-01-01 to 2023-12-31

DATA SUMMARY STATISTICS
======================================================================
Total Days:                   365
  - Weekdays:                 261
  - Weekends:                 104
------
Hourly Energy Consumption (kWh):
  - Min:                      10.00
  - Max:                      89.45
  - Mean:                     48.32
  - StdDev:                   18.75
======================================================================

STEP 2: K-Means Clustering Analysis
------
✓ Clustering completed!
  K-Means with 3 clusters

Cluster Distribution:
  Low      (Cluster 0) - 104 days (28.5%)
  Medium   (Cluster 1) - 156 days (42.7%)
  High     (Cluster 2) - 105 days (28.8%)
```

---

### **Method 3: Custom Python Script**

Best for: Advanced users, integration, custom workflows

Create a Python file and use the modules:

```python
from src.data_loader import EnergyDataLoader
from src.clustering import EnergyClusterer
from src.regression import EnergyRegressor
from src.utils import calculate_savings_potential, print_metrics

# === LOAD DATA ===
loader = EnergyDataLoader()
loader.load_data('data/energy_data.csv')
daily_data = loader.get_daily_data()
loader.print_summary()

# === CLUSTERING ===
clusterer = EnergyClusterer()
clusterer.fit(daily_data, n_clusters=3)
clusterer.print_cluster_summary()
labeled_data = clusterer.get_labeled_data()

# === FORECASTING ===
regressor = EnergyRegressor()
regressor.fit(labeled_data, degree=2)
regressor.forecast(days_into_future=30)
regressor.print_forecast_summary()

# === SAVINGS ANALYSIS ===
weekday_data = daily_data[daily_data['Day_Type'] == 'Weekday']
weekend_data = daily_data[daily_data['Day_Type'] == 'Weekend']

metrics = calculate_savings_potential(
    weekday_data['Daily_Avg'].mean(),
    weekend_data['Daily_Avg'].mean()
)
print_metrics(metrics)

# === VISUALIZATIONS ===
fig1 = clusterer.visualize_clusters()
fig2 = regressor.visualize_forecasts(labeled_data)

import matplotlib.pyplot as plt
plt.show()
```

---

## 📊 Understanding the Analysis

### **1. Data Loading & Preprocessing**

**Input CSV Format:**
```csv
Date,Day,Hour,Energy_Consumption
2023-01-01,Sunday,0,18.45
2023-01-01,Sunday,1,16.82
2023-01-02,Monday,0,28.34
```

**Processing Steps:**
- ✅ Parse dates and validate formats
- ✅ Handle missing values
- ✅ Remove duplicate records
- ✅ Calculate daily aggregates (Total, Average, Min, Max)
- ✅ Classify days as Weekday/Weekend

**Output:**
- Hourly data (raw)
- Daily summary statistics
- Weekend vs Weekday comparison

### **2. K-Means Clustering**

**What it does:**
Identifies three distinct energy usage patterns in the building

**Three Clusters:**
```
🟢 LOW Usage (typically 28% of days)
   - Weekend days
   - Nights and early mornings
   - Minimal consumption
   - Example: 20-40 kWh/day

🟠 MEDIUM Usage (typically 43% of days)
   - Partial business operation
   - Moderate demand periods
   - Example: 40-60 kWh/day

🔴 HIGH Usage (typically 29% of days)
   - Peak business hours
   - Maximum occupancy
   - AC/Heating running heavily
   - Example: 60-90 kWh/day
```

**Features Used:**
- Daily Average consumption
- Daily Total consumption

**Algorithm:**
- K-Means algorithm (sklearn)
- 10 random initializations for stability
- Automatic convergence

**Output:**
- Cluster assignments for each day
- Cluster centers and characteristics
- Visualization scatter plot

### **3. Polynomial Regression & Forecasting**

**What it does:**
Predicts future energy consumption for each cluster

**Regression Models:**
```
Degree 1: Linear trend (y = mx + b)
          Best for: Steady, predictable patterns
          
Degree 2: Quadratic curve (y = ax² + bx + c)
          Best for: Non-linear trends (RECOMMENDED)
          
Degree 3: Cubic curve (y = ax³ + bx² + cx + d)
          Best for: Complex patterns with reversals
```

**Process:**
1. Separate data by cluster
2. Create sequential time index (days)
3. Fit polynomial features
4. Train linear regression model
5. Generate 30-day forecasts
6. Calculate performance metrics

**Metrics:**
- **R² Score**: How well model fits (0-1, higher is better)
- **RMSE**: Root Mean Squared Error (lower is better)
- **MAE**: Mean Absolute Error (lower is better)

**Output:**
- Individual forecasts for each cluster
- Performance metrics
- Visualization with historical + forecast

### **4. Savings Potential Analysis**

**Calculation:**
```
Weekend Dip = (Weekday Avg - Weekend Avg) / Weekday Avg × 100%

Weekday Potential = Weekday Avg - Target Usage
Weekend Potential = Weekend Avg - Target Usage

Target = Weekend Average Consumption (most efficient baseline)
```

**Example Results:**
```
Weekday Average:        65.42 kWh
Weekend Average:        35.18 kWh
Weekend Dip:           46.20%  (this is the key metric!)

Potential Savings on Weekdays: 30.24 kWh (46.20%)
If weekdays matched weekend efficiency, could save:
  - Daily: 30.24 kWh
  - Monthly: 905 kWh (assuming 30 weekdays)
  - Annually: 10,860 kWh
```

---

## 📈 Key Outputs & Metrics

### **Dashboard Displays:**

```
📊 Data Summary
  - Total days analyzed
  - Weekday/Weekend breakdown
  - Average hourly consumption
  
📍 Clustering
  - Scatter plot (color-coded by cluster)
  - Pie chart (cluster distribution)
  - Summary statistics table
  
📉 Weekday vs Weekend
  - Bar chart comparison
  - Weekend dip percentage
  - Immediate savings potential
  
🔮 Forecasting
  - Line charts per cluster
  - Historical + forecast overlay
  - Trend indicators
  - Model performance metrics
  
💰 Savings
  - Current usage breakdown
  - Savings potential (kWh & %)
  - Target usage goals
  - Detailed metrics table
  
📋 Data Views
  - Daily summary (first 50 days)
  - Detailed daily with clusters
  - Hourly raw data
```

---

## 🎓 Interpretation Guide

### **How to Read the Clustering Scatter Plot:**

```
Y-axis: Daily Total Consumption (kWh)
X-axis: Daily Average Consumption (kWh)

Points:
  ● = Weekday (circle)
  ■ = Weekend (square)
  
Colors:
  🟢 = Low usage cluster
  🟠 = Medium usage cluster
  🔴 = High usage cluster
  
★ = Cluster centers (optimal point for each cluster)

Interpretation:
  - Widely spread = Inconsistent usage patterns
  - Tight clusters = Consistent patterns
  - Clear separation = Well-defined usage groups
```

### **How to Read the Forecast Line Chart:**

```
Solid line  = Historical actual consumption
Dashed line = Forecasted consumption

Vertical dotted line = Split between history and forecast

Interpretation:
  - Ascending trend = Energy usage increasing (may need intervention)
  - Descending trend = Energy usage decreasing (good!)
  - Horizontal line = Stable, consistent usage
```

### **R² Score Interpretation:**

```
R² = 0.95-1.0   Excellent fit (model is very accurate)
R² = 0.85-0.95  Very good fit (model is quite accurate)
R² = 0.70-0.85  Good fit (model is acceptable)
R² = 0.50-0.70  Fair fit (consider different approach)
R² < 0.50       Poor fit (model needs improvement)
```

---

## ⏱️ Typical Execution Times

| Task | Time | Notes |
|------|------|-------|
| Install packages | 3-5 min | One-time setup |
| Generate sample data | 2-5 sec | 365 days = 8760 records |
| Load 1-year data | 1-2 sec | ~8,760 hourly records |
| K-Means clustering | 1-2 sec | 3 clusters on 365 days |
| Polynomial regression | 2-3 sec | Multiple models (degree 1-3) |
| Dashboard startup | 5-10 sec | Streamlit initialization |
| Dashboard interaction | Real-time | <1 second per parameter change |
| Full analysis script | 30-45 sec | All steps + visualizations |

---

## 🔍 Troubleshooting

### **Issue: Import Error for src modules**

```
ModuleNotFoundError: No module named 'src'
```

**Solution:**
- Run from project root directory
- Verify `src/__init__.py` exists
- Check Python path: `import sys; print(sys.path)`

### **Issue: Streamlit "Address already in use"**

```
Error: Address already in use.  Streamlit tried to bind to port 8501.
```

**Solution:**
```bash
streamlit run dashboard.py --server.port 8502
```

Or kill existing process:
```bash
# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:8501 | xargs kill -9
```

### **Issue: Not finding data file**

```
FileNotFoundError: Data file not found: data/energy_data.csv
```

**Solution:**
```bash
python generate_sample_data.py
```

### **Issue: CSV parsing error**

```
Error parsing CSV - unexpected number of columns
```

**Solution:**
- Verify CSV has exactly 4 columns: Date, Day, Hour, Energy_Consumption
- Check for empty rows at bottom of file
- Use UTF-8 encoding
- Avoid special characters in column names

---

## 🎯 Common Use Cases

### **Use Case 1: Understand Building Patterns**

**Steps:**
1. Run `streamlit run dashboard.py`
2. Upload your latest 1-month data
3. Check "Weekday vs Weekend" section
4. Note the weekend dip percentage
5. Compare to industry standards

### **Use Case 2: Forecast Next Month**

**Steps:**
1. Run `python analysis_example.py`
2. Check "STEP 3: Regression & Forecasting" output
3. Review forecast trends by cluster
4. Use forecasts for scheduling maintenance

### **Use Case 3: Identify Savings Opportunities**

**Steps:**
1. Run `streamlit run dashboard.py`
2. Check "Savings Potential Analysis" section
3. Note weekday savings potential (in kWh and %)
4. Calculate annual savings
5. Plan interventions for high-demand periods

### **Use Case 4: Automate Weekly Reports**

**Steps:**
1. Upload latest week's data to CSV
2. Run `python analysis_example.py`
3. Review generated PNG images
4. Email reports to stakeholders
5. Schedule automatically with Task Scheduler/cron

---

## 💡 Tips for Best Results

### **Data Quality:**
✅ Ensure complete 24-hour data for each day  
✅ Remove outliers (sensor errors, anomalies)  
✅ Use consistent kWh units  
✅ Include at least 30 days for reliable clustering  

### **Clustering:**
✅ Use 3 clusters for typical buildings  
✅ Increase to 4-5 for buildings with multiple shifts  
✅ Review scatter plot for clear cluster separation  

### **Forecasting:**
✅ Use degree 2 (quadratic) by default  
✅ Choose degree 1 for steady trends  
✅ Use degree 3 only for complex patterns  
✅ Compare R² scores to validate fit  

### **Savings Analysis:**
✅ Set realistic targets (e.g., 20% reduction)  
✅ Focus on high-impact periods (peak hours)  
✅ Implement changes gradually  
✅ Measure actual vs. forecasted savings  

---

## 🚀 Advanced Features

### **Feature Engineering:**
```python
# Add custom features
daily_data['Day_Num'] = range(len(daily_data))
daily_data['Week_Num'] = daily_data['Day_Num'] // 7
daily_data['Is_Holiday'] = 0  # Mark holidays
```

### **Multiple Models:**
```python
# Compare different degrees
for degree in [1, 2, 3]:
    reg = EnergyRegressor()
    reg.fit(daily_data, degree=degree)
    metrics = reg.get_metrics()
    print(f"Degree {degree}: R²={metrics['r2_score']}")
```

### **Seasonal Analysis:**
```python
# Analyze by quarter
for quarter in ['Q1', 'Q2', 'Q3', 'Q4']:
    q_data = daily_data[daily_data['Quarter'] == quarter]
    clusterer = EnergyClusterer()
    clusterer.fit(q_data, n_clusters=3)
```

---

## 📞 Need Help?

**Check These Resources:**
1. **README.md** - Comprehensive documentation
2. **QUICKSTART.md** - 5-minute setup guide
3. **Code Comments** - Detailed explanations in each module
4. **analysis_example.py** - Complete working example

**Key Files & Their Purpose:**
```
src/data_loader.py   → How to load and process CSV files
src/clustering.py    → How K-Means works on energy data
src/regression.py    → How forecasting models are trained
src/utils.py         → Helper functions and calculations
dashboard.py         → Interactive web interface
analysis_example.py  → Complete pipeline example
```

---

## ✅ Verification Checklist

Before running analysis:

- [ ] Python 3.8+ installed (`python --version`)
- [ ] All packages installed (`pip list | grep pandas`)
- [ ] Project files in correct location
- [ ] CSV file has correct format (Date, Day, Hour, Energy_Consumption)
- [ ] CSV file has at least 30 days of data
- [ ] No special characters in CSV
- [ ] data/ directory exists

Before sharing results:

- [ ] Verified sample data is representative
- [ ] Checked clustering for clear separation
- [ ] Confirmed R² score > 0.70
- [ ] Reviewed forecasts for reasonableness
- [ ] Documented any data preprocessing done
- [ ] Validated calculations against expected outputs

---

## 🎉 You're Ready!

Everything is configured and ready to execute. Choose your method:

### **Quick Start (5 min):**
```bash
streamlit run dashboard.py
```

### **Full Analysis (2 min):**
```bash
python analysis_example.py
```

### **Custom Script:**
Create your own `.py` file using the modules.

---

**Happy analyzing! Let the data tell its story about your building's energy patterns.** ⚡📊

Last Updated: February 2024  
Version: 1.0.0  
Status: Production Ready ✅
