# 📈 Time-Series Usage Analysis & Forecast Dashboard

A fully interactive data science dashboard built with **Streamlit**, **Prophet**, and **Scikit-learn** for time-series usage analysis, forecasting, and ML-powered category prediction.

---

## 🚀 Features

| Feature | Details |
|---|---|
| **Data Input** | Upload your own CSV or use the built-in auto-generated sample |
| **Historical Visualization** | Interactive line charts with rolling averages, ±1σ bands, day-of-week heatmaps |
| **Prophet Forecasting** | 7–90 day forecasts with 95 % confidence intervals |
| **What-If Scenario Tool** | Timeline slider to query any predicted future day |
| **Naive Bayes Classifier** | Predicts Low / Medium / High usage with real-time probability bars |
| **KPI Metrics** | Total records, average usage, peak usage, date range |

---

## 📁 File Structure

```
project/
│
├── app.py                  # Main Streamlit dashboard
├── model.py                # ML logic (Naive Bayes + Prophet)
├── data/
│   ├── sample_usage.csv    # Auto-generated sample dataset
│   └── generate_sample.py  # Script to regenerate sample data
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## 🔧 Setup & Run

### 1 — Clone / download this project

```bash
cd project
```

### 2 — (Recommended) Create a virtual environment

```bash
python -m venv venv
# macOS / Linux
source venv/bin/activate
# Windows
venv\Scripts\activate
```

### 3 — Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `prophet` requires `pystan` or `cmdstanpy`.  
> On some systems you may need to run:  
> `pip install pystan==2.19.1.1` before installing prophet.

### 4 — Run the dashboard

```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`.

---

## 📂 CSV Format (for custom upload)

Your CSV must contain **exactly these three columns**:

| Column | Type | Example |
|--------|------|---------|
| `date` | YYYY-MM-DD string | `2024-01-15` |
| `usage` | Numeric | `142.7` |
| `category` | Low / Medium / High | `Medium` |

---

## 🧠 ML Details

### Gaussian Naive Bayes
- Feature: raw `usage` value  
- Target: `category` (Low / Medium / High)  
- 80 / 20 train-test split  
- Outputs accuracy score and full classification report  

### Prophet Time-Series Forecasting
- Weekly + yearly seasonality enabled  
- 95 % confidence intervals  
- Forecast horizon: 7–90 days (adjustable via sidebar slider)  

---

## 📦 Tech Stack

- [Streamlit](https://streamlit.io/) – dashboard framework  
- [Prophet](https://facebook.github.io/prophet/) – time-series forecasting  
- [Scikit-learn](https://scikit-learn.org/) – Naive Bayes classification  
- [Plotly](https://plotly.com/python/) – interactive charts  
- [Pandas](https://pandas.pydata.org/) – data manipulation  
- [NumPy](https://numpy.org/) – numerical computing  

---

## 📸 Dashboard Sections

1. **Overview** – KPI cards + raw data preview  
2. **Historical Usage** – line chart + category pie + heatmap  
3. **Prophet Forecast** – full forecast with CI ribbon  
4. **What-If Scenario Tool** – day-level future prediction lookup  
5. **Naive Bayes Predictor** – interactive usage slider + probability bars  

---

*Built with ❤️ using open-source tools.*
