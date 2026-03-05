# 🚦 Traffic Light Usage Optimizer

Streamlit dashboard using **Polynomial Regression** to predict traffic light green duration from sensor vehicle counts, with real-time bar charts and anomaly detection alerts.

## 📁 Structure
```
traffic_light/
├── app.py                  ← Streamlit dashboard (main entry)
├── requirements.txt
├── data/
│   ├── generate_data.py    ← Synthetic sensor data generator
│   └── sensor_data.csv     ← auto-generated on first run
└── models/
    └── poly_model.py       ← Polynomial regression + anomaly detection
```

## 🚀 Run in VS Code

Open PowerShell terminal inside the `traffic_light` folder:

```powershell
python -m venv venv
```
```powershell
venv\Scripts\activate
```
```powershell
pip install -r requirements.txt
```
```powershell
streamlit run app.py
```

## 🎛 Dashboard Features

| Tab | Description |
|-----|-------------|
| 📊 **Real-Time Bar Chart** | Live vehicle count + predicted green duration bars with anomaly highlights. Enable Real-Time Mode in sidebar for simulation. |
| 📈 **Regression Curve** | Scatter plot + polynomial curve showing vehicle count → green duration mapping. Residual plot included. |
| 🚨 **Anomaly Monitor** | Z-score time series, anomaly counts per intersection, full anomaly table |
| 🏙️ **Intersection Comparison** | Heatmap, box plots, summary stats across all 5 intersections |

## Sidebar Controls
- Intersection selector
- Hour range filter
- Day type (All / Weekdays / Weekends)
- Polynomial degree (2, 3, 4)
- Anomaly Z-score threshold
- Rolling window size
- Real-Time simulation toggle
- Manual prediction tool with gauge
