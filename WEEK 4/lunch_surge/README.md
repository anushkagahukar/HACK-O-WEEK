# 🍽️ Lunch Surge Predictor

Streamlit dashboard using **Linear Regression** to predict lunch-hour crowd surges from weather/temperature data, with a **real-time WebSocket line chart**.

## 📁 Structure
```
lunch_surge/
├── app.py                  ← Streamlit dashboard
├── websocket_server.py     ← WebSocket server (run separately)
├── requirements.txt
├── data/
│   ├── generate_data.py    ← Synthetic data generator
│   └── lunch_data.csv      ← auto-generated on first run
└── models/
    └── regression_model.py ← Linear regression + feature importance
```

## 🚀 Run in VS Code

### Terminal 1 — Start the dashboard:
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

### Terminal 2 — Start WebSocket server (optional, for live data):
```powershell
venv\Scripts\activate
python websocket_server.py
```

Then click **Connect WebSocket** in the sidebar.

## 🎛 Dashboard Tabs

| Tab | Description |
|-----|-------------|
| ⚡ **Real-Time WebSocket** | Live line chart from WebSocket feed. Built-in simulation if server not running. |
| 📈 **Regression Analysis** | Actual vs predicted scatter, feature importance, hourly prediction curves |
| 🌡️ **Weather Impact** | Surge by weather condition, temperature scatter, heatmap |
| 🏪 **Location Breakdown** | Bar, box plots, hourly trend per location |
