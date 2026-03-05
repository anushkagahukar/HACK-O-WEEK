"""
app.py — Lunch Surge Prediction Dashboard
Linear Regression · Weather Data · Real-Time WebSocket Line Chart
"""

import os
import sys
import json
import time
import asyncio
import threading
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import websockets

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data.generate_data import generate_data, LOCATIONS, WEATHER_CONDITIONS
from models.regression_model import train_model, predict_surge, get_feature_importance

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🍽️ Lunch Surge Predictor",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
body, .main { background-color: #0f1117; }
h1 { color: #f97316 !important; }
h2, h3 { color: #fdba74 !important; }
div[data-testid="stSidebar"] { background-color: #0d1b2a; }
.card {
    background: linear-gradient(135deg, #1c1207, #2d1a00);
    border: 1px solid #7c2d12;
    border-radius: 14px;
    padding: 16px 20px;
    text-align: center;
    margin-bottom: 6px;
}
.card-label { color: #fdba74; font-size: 0.75rem; font-weight: 700;
              text-transform: uppercase; letter-spacing: 1px; }
.card-value { color: #ffffff; font-size: 1.9rem; font-weight: 800; margin-top: 4px; }
.card-sub   { color: #6b7280; font-size: 0.72rem; margin-top: 2px; }
.ws-connected    { background:#052e16; border:1px solid #22c55e; border-radius:8px;
                   padding:8px 14px; color:#86efac; font-size:0.82rem; }
.ws-disconnected { background:#3b0a0a; border:1px solid #ef4444; border-radius:8px;
                   padding:8px 14px; color:#fca5a5; font-size:0.82rem; }
</style>
""", unsafe_allow_html=True)

LOCATION_COLORS = {
    "Cafeteria A":  "#f97316",
    "Food Court B": "#60a5fa",
    "Restaurant C": "#4ade80",
    "Canteen D":    "#a78bfa",
}
WEATHER_ICONS = {"Sunny":"☀️","Cloudy":"☁️","Rainy":"🌧️","Windy":"💨","Snowy":"❄️"}

# ── Load & cache data + model ──────────────────────────────────────────────────
@st.cache_data
def load_data():
    os.makedirs("data", exist_ok=True)
    if os.path.exists("data/lunch_data.csv"):
        return pd.read_csv("data/lunch_data.csv", parse_dates=["date"])
    return generate_data()

@st.cache_resource
def load_model():
    df = load_data()
    return train_model(df)

df_raw = load_data()
pipeline, metrics = load_model()

# ── Session state for real-time data ──────────────────────────────────────────
if "rt_data" not in st.session_state:
    st.session_state.rt_data = []
if "ws_connected" not in st.session_state:
    st.session_state.ws_connected = False
if "ws_error" not in st.session_state:
    st.session_state.ws_error = ""

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🍽️ Controls")
    st.divider()

    selected_location = st.selectbox("📍 Location", ["All"] + LOCATIONS)

    st.markdown("**📅 Day Type**")
    day_type = st.radio("", ["All", "Weekdays", "Weekends"], index=0, label_visibility="collapsed")

    st.markdown("**🌡️ Temperature Range (°C)**")
    temp_range = st.slider("", -5, 40, (-5, 40), label_visibility="collapsed")

    st.divider()
    st.markdown("**🔮 Manual Prediction**")
    pred_temp     = st.slider("Temperature (°C)", -5, 40, 22)
    pred_weather  = st.selectbox("Weather", WEATHER_CONDITIONS)
    pred_hour     = st.slider("Hour", 9, 15, 12)
    pred_location = st.selectbox("Location", LOCATIONS)
    pred_humidity = st.slider("Humidity (%)", 20, 100, 60)
    pred_wind     = st.slider("Wind Speed (km/h)", 0, 50, 10)
    pred_weekend  = st.checkbox("Is Weekend?", value=False)

    st.divider()
    st.markdown("**⚡ WebSocket Settings**")
    ws_url = st.text_input("WebSocket URL", value="ws://localhost:8765")
    connect_ws = st.button("🔌 Connect WebSocket", use_container_width=True)
    fetch_count = st.slider("Readings to fetch", 5, 50, 20)

# ── Filter data ────────────────────────────────────────────────────────────────
df = df_raw.copy()
if selected_location != "All":
    df = df[df["location"] == selected_location]
if day_type == "Weekdays":
    df = df[df["is_weekend"] == 0]
elif day_type == "Weekends":
    df = df[df["is_weekend"] == 1]
df = df[(df["temperature"] >= temp_range[0]) & (df["temperature"] <= temp_range[1])]

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🍽️ Lunch Surge Predictor")
st.caption("Linear Regression · Weather-Driven · Real-Time WebSocket Updates")
st.divider()

# ── Manual prediction result ───────────────────────────────────────────────────
feels_like_pred = pred_temp - 0.3 * pred_wind
manual_pred = predict_surge(
    pipeline, pred_temp, feels_like_pred, pred_humidity,
    pred_wind, pred_hour, int(pred_weekend),
    pd.Timestamp("today").month, pred_weather, pred_location,
)

# ── KPI Cards ──────────────────────────────────────────────────────────────────
avg_surge  = df["surge_count"].mean()
peak_surge = df["surge_count"].max()
peak_hour  = df.groupby("hour")["surge_count"].mean().idxmax()
busy_loc   = df.groupby("location")["surge_count"].mean().idxmax() if selected_location == "All" else selected_location

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="card">
        <div class="card-label">Avg Lunch Surge</div>
        <div class="card-value">{avg_surge:.0f}</div>
        <div class="card-sub">people / reading</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="card">
        <div class="card-label">Peak Surge</div>
        <div class="card-value">{peak_surge:,}</div>
        <div class="card-sub">max recorded</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="card">
        <div class="card-label">Busiest Hour</div>
        <div class="card-value">{peak_hour}:00</div>
        <div class="card-sub">peak lunch hour</div>
    </div>""", unsafe_allow_html=True)
with c4:
    color = "#ef4444" if manual_pred > 250 else "#fbbf24" if manual_pred > 150 else "#4ade80"
    st.markdown(f"""<div class="card">
        <div class="card-label">Your Prediction</div>
        <div class="card-value" style="color:{color}">{manual_pred}</div>
        <div class="card-sub">{pred_location} @ {pred_hour}:00</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "⚡ Real-Time WebSocket",
    "📈 Regression Analysis",
    "🌡️ Weather Impact",
    "🏪 Location Breakdown",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — REAL-TIME WEBSOCKET LINE CHART
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("⚡ Real-Time Lunch Surge — WebSocket Feed")

    # WebSocket connection handler
    if connect_ws:
        async def fetch_ws_data(url, n):
            readings = []
            try:
                async with websockets.connect(url, open_timeout=3) as ws:
                    for _ in range(n):
                        msg = await asyncio.wait_for(ws.recv(), timeout=3)
                        data = json.loads(msg)
                        readings.extend(data)
                return readings, True, ""
            except Exception as e:
                return [], False, str(e)

        with st.spinner("Connecting to WebSocket..."):
            try:
                loop = asyncio.new_event_loop()
                data, connected, err = loop.run_until_complete(
                    fetch_ws_data(ws_url, fetch_count)
                )
                loop.close()
                if connected and data:
                    st.session_state.rt_data = data
                    st.session_state.ws_connected = True
                    st.session_state.ws_error = ""
                else:
                    st.session_state.ws_connected = False
                    st.session_state.ws_error = err
            except Exception as e:
                st.session_state.ws_connected = False
                st.session_state.ws_error = str(e)

    # Connection status
    if st.session_state.ws_connected:
        st.markdown('<div class="ws-connected">🟢 WebSocket Connected — Live data received</div>',
                    unsafe_allow_html=True)
    elif st.session_state.ws_error:
        st.markdown(f'<div class="ws-disconnected">🔴 Not Connected — {st.session_state.ws_error[:80]}<br>'
                    f'<b>Start the server first:</b> python websocket_server.py</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<div class="ws-disconnected">⚪ Not connected — click "Connect WebSocket" in sidebar.<br>'
                    'Start server with: <b>python websocket_server.py</b></div>',
                    unsafe_allow_html=True)

    st.markdown("")

    # Use WebSocket data if available, else simulate from historical
    if st.session_state.rt_data:
        rt_df = pd.DataFrame(st.session_state.rt_data)
        data_source = "🔴 LIVE — WebSocket"
    else:
        # Simulate real-time from last 30 minutes of historical data
        sim = df[df["hour"].isin([11, 12, 13, 14])].tail(80).copy()
        sim["timestamp"] = [f"{12}:{str(i*2).zfill(2)}:{str(i%30).zfill(2)}" for i in range(len(sim))]
        sim = sim.rename(columns={"surge_count": "surge_count"})
        rt_df = sim[["timestamp", "location", "surge_count", "temperature", "humidity", "wind_speed", "weather"]].copy()
        data_source = "📊 SIMULATED — Historical data"

    st.caption(f"Data source: {data_source}")

    # Real-time line chart
    fig_rt = go.Figure()
    for loc in LOCATIONS:
        loc_df = rt_df[rt_df["location"] == loc] if "location" in rt_df.columns else rt_df
        if len(loc_df) == 0:
            continue
        fig_rt.add_trace(go.Scatter(
            x=loc_df["timestamp"] if "timestamp" in loc_df.columns else list(range(len(loc_df))),
            y=loc_df["surge_count"],
            mode="lines+markers",
            name=loc,
            line=dict(color=LOCATION_COLORS[loc], width=2),
            marker=dict(size=5),
        ))

    fig_rt.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0f1117",
        plot_bgcolor="#0d1b2a",
        title="Live Surge Count per Location",
        xaxis_title="Time",
        yaxis_title="People Count",
        height=420,
        margin=dict(l=40, r=20, t=60, b=60),
        legend=dict(orientation="h", y=-0.2),
    )
    fig_rt.update_xaxes(tickangle=-30)
    st.plotly_chart(fig_rt, use_container_width=True)

    # Live weather ticker
    if len(rt_df) > 0:
        latest = rt_df.iloc[-1]
        w1, w2, w3, w4 = st.columns(4)
        w1.metric("🌡️ Temperature", f"{latest.get('temperature', 'N/A')}°C")
        w2.metric("💧 Humidity",    f"{latest.get('humidity', 'N/A')}%")
        w3.metric("💨 Wind Speed",  f"{latest.get('wind_speed', 'N/A')} km/h")
        w4.metric("🌤️ Weather",     f"{WEATHER_ICONS.get(str(latest.get('weather','')),'')} {latest.get('weather','N/A')}")

    # Auto-refresh simulation
    st.divider()
    st.markdown("#### 🔄 Simulated Real-Time Stream (no server needed)")
    if st.button("▶ Run 10-step live simulation"):
        placeholder = st.empty()
        sim_df = df[df["hour"].isin([11,12,13,14])].sample(100, random_state=42).reset_index(drop=True)
        rolling = {loc: [] for loc in LOCATIONS}
        for i in range(min(50, len(sim_df))):
            row = sim_df.iloc[i]
            rolling[row["location"]].append(row["surge_count"])
            fig_sim = go.Figure()
            for loc in LOCATIONS:
                if rolling[loc]:
                    fig_sim.add_trace(go.Scatter(
                        y=rolling[loc], mode="lines+markers",
                        name=loc,
                        line=dict(color=LOCATION_COLORS[loc], width=2),
                        marker=dict(size=5),
                    ))
            fig_sim.update_layout(
                template="plotly_dark", paper_bgcolor="#0f1117", plot_bgcolor="#0d1b2a",
                title=f"Step {i+1}/50 — Streaming...",
                xaxis_title="Reading", yaxis_title="Surge Count",
                height=380, margin=dict(l=40, r=20, t=50, b=40),
                legend=dict(orientation="h", y=-0.2),
            )
            placeholder.plotly_chart(fig_sim, use_container_width=True)
            time.sleep(0.15)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — REGRESSION ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader(f"Linear Regression Model")
    st.markdown(f"**MAE:** `{metrics['MAE']}` &nbsp; **RMSE:** `{metrics['RMSE']}` &nbsp; **R²:** `{metrics['R2']}`")

    r1, r2 = st.columns(2)

    # Actual vs predicted scatter
    sample = df.sample(min(2000, len(df)), random_state=0)
    feat_cols = ["temperature","feels_like","humidity","wind_speed","hour","is_weekend","month","weather","location"]
    sample_pred = np.clip(pipeline.predict(sample[feat_cols]), 0, None)

    with r1:
        fig_scatter = go.Figure()
        fig_scatter.add_trace(go.Scatter(
            x=sample["surge_count"], y=sample_pred,
            mode="markers",
            marker=dict(color="#f97316", size=4, opacity=0.5),
            name="Actual vs Predicted",
        ))
        max_val = max(sample["surge_count"].max(), sample_pred.max())
        fig_scatter.add_trace(go.Scatter(
            x=[0, max_val], y=[0, max_val],
            mode="lines", name="Perfect Fit",
            line=dict(color="#ffffff", dash="dash", width=1.5),
        ))
        fig_scatter.update_layout(
            template="plotly_dark", paper_bgcolor="#0f1117",
            title="Actual vs Predicted Surge",
            xaxis_title="Actual", yaxis_title="Predicted",
            height=400, margin=dict(l=40, r=20, t=50, b=40),
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    # Feature importance
    with r2:
        importance = get_feature_importance(pipeline)
        fig_imp = px.bar(
            importance, x="AbsCoef", y="Feature", orientation="h",
            color="Coefficient",
            color_continuous_scale="RdYlGn",
            title="Top Feature Coefficients",
        )
        fig_imp.update_layout(
            template="plotly_dark", paper_bgcolor="#0f1117",
            height=400, margin=dict(l=20, r=20, t=50, b=40),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_imp, use_container_width=True)

    # Hourly prediction curve
    st.markdown("#### Predicted Surge by Hour — Temperature Effect")
    hours = list(range(9, 16))
    temps_to_show = [5, 15, 22, 30, 38]
    fig_curve = go.Figure()
    for t in temps_to_show:
        preds = [predict_surge(pipeline, t, t-3, 60, 10, h, 0,
                               pd.Timestamp("today").month, "Sunny", "Food Court B")
                 for h in hours]
        fig_curve.add_trace(go.Scatter(
            x=hours, y=preds, mode="lines+markers",
            name=f"{t}°C",
            line=dict(width=2),
        ))
    fig_curve.update_layout(
        template="plotly_dark", paper_bgcolor="#0f1117", plot_bgcolor="#0d1b2a",
        title="Surge Prediction by Hour at Different Temperatures (Food Court B, Sunny)",
        xaxis_title="Hour", yaxis_title="Predicted People",
        height=380, margin=dict(l=40, r=20, t=60, b=40),
        legend_title="Temp",
    )
    st.plotly_chart(fig_curve, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — WEATHER IMPACT
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("🌡️ Weather Impact on Lunch Surge")

    w1, w2 = st.columns(2)

    with w1:
        # Avg surge by weather condition
        weather_avg = df.groupby("weather")["surge_count"].mean().reset_index()
        weather_avg["icon"] = weather_avg["weather"].map(WEATHER_ICONS)
        weather_avg["label"] = weather_avg["icon"] + " " + weather_avg["weather"]
        fig_weather = px.bar(
            weather_avg, x="label", y="surge_count",
            color="surge_count", color_continuous_scale="Oranges",
            title="Avg Surge by Weather Condition",
            labels={"surge_count": "Avg People", "label": ""},
        )
        fig_weather.update_layout(
            template="plotly_dark", paper_bgcolor="#0f1117",
            height=380, showlegend=False,
            margin=dict(l=20, r=20, t=50, b=40),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_weather, use_container_width=True)

    with w2:
        # Temperature scatter
        fig_temp = px.scatter(
            df.sample(min(3000, len(df)), random_state=1),
            x="temperature", y="surge_count",
            color="weather",
            trendline="ols",
            title="Temperature vs Surge Count",
            labels={"surge_count": "People", "temperature": "°C"},
            opacity=0.5,
        )
        fig_temp.update_layout(
            template="plotly_dark", paper_bgcolor="#0f1117",
            height=380, margin=dict(l=20, r=20, t=50, b=40),
        )
        st.plotly_chart(fig_temp, use_container_width=True)

    # Heatmap: temp bin × hour
    st.markdown("#### Heatmap: Temperature Range × Hour")
    df["temp_bin"] = pd.cut(df["temperature"], bins=[-5,0,10,20,30,40],
                             labels=["<0°C","0-10°C","10-20°C","20-30°C","30+°C"])
    pivot = df.groupby(["temp_bin","hour"])["surge_count"].mean().reset_index()
    pivot_table = pivot.pivot(index="temp_bin", columns="hour", values="surge_count")
    fig_hm = px.imshow(
        pivot_table, color_continuous_scale="Oranges",
        title="Avg Surge — Temperature × Hour",
        labels=dict(x="Hour", y="Temperature", color="People"),
        aspect="auto",
    )
    fig_hm.update_layout(
        template="plotly_dark", paper_bgcolor="#0f1117",
        height=340, margin=dict(l=20, r=20, t=50, b=40),
    )
    st.plotly_chart(fig_hm, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — LOCATION BREAKDOWN
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("🏪 Location-Level Breakdown")

    loc_stats = (
        df.groupby("location")["surge_count"]
        .agg(["mean","max","std"])
        .round(1)
        .reset_index()
    )
    loc_stats.columns = ["Location","Avg Surge","Peak Surge","Std Dev"]

    l1, l2 = st.columns(2)
    with l1:
        fig_loc = px.bar(
            loc_stats, x="Location", y="Avg Surge",
            color="Location", color_discrete_map=LOCATION_COLORS,
            title="Average Surge per Location",
        )
        fig_loc.update_layout(
            template="plotly_dark", paper_bgcolor="#0f1117",
            height=360, showlegend=False,
            margin=dict(l=20, r=20, t=50, b=40),
        )
        st.plotly_chart(fig_loc, use_container_width=True)

    with l2:
        fig_box = px.box(
            df, x="location", y="surge_count",
            color="location", color_discrete_map=LOCATION_COLORS,
            title="Surge Distribution by Location",
            points="outliers",
        )
        fig_box.update_layout(
            template="plotly_dark", paper_bgcolor="#0f1117",
            height=360, showlegend=False,
            margin=dict(l=20, r=20, t=50, b=40),
        )
        st.plotly_chart(fig_box, use_container_width=True)

    # Hourly trend per location
    hourly_loc = df.groupby(["hour","location"])["surge_count"].mean().reset_index()
    fig_hourly = px.line(
        hourly_loc, x="hour", y="surge_count", color="location",
        color_discrete_map=LOCATION_COLORS,
        markers=True,
        title="Avg Surge by Hour per Location",
        labels={"surge_count":"Avg People","hour":"Hour"},
    )
    fig_hourly.update_layout(
        template="plotly_dark", paper_bgcolor="#0f1117", plot_bgcolor="#0d1b2a",
        height=360, margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(orientation="h", y=-0.2),
    )
    st.plotly_chart(fig_hourly, use_container_width=True)

    st.markdown("#### Summary Table")
    st.dataframe(loc_stats, use_container_width=True, hide_index=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<center><small>🍽️ Lunch Surge Predictor · Linear Regression · WebSocket · Streamlit + Plotly</small></center>",
    unsafe_allow_html=True,
)
