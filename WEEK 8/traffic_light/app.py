venv\Scripts\activate"""
app.py — Traffic Light Usage Dashboard
Polynomial Regression · Real-Time Bar Chart · Anomaly Alerts
"""

import os
import sys
import time
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data.generate_data import generate_sensor_data, INTERSECTIONS
from models.poly_model import (
    train_poly_model,
    predict_light,
    detect_anomalies,
    vehicle_to_light_duration,
    build_features,
)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🚦 Traffic Light Optimizer",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
body, .main { background-color: #0b0f1a; }
h1 { color: #4ade80 !important; letter-spacing: 1px; }
h2, h3 { color: #86efac !important; }
div[data-testid="stSidebar"] { background-color: #0d1b2a; }
.card {
    background: linear-gradient(135deg, #0f2027, #1a3a2a);
    border: 1px solid #1e4d2b;
    border-radius: 14px;
    padding: 16px 20px;
    text-align: center;
    margin-bottom: 6px;
}
.card-label { color: #86efac; font-size: 0.75rem; font-weight: 700;
              text-transform: uppercase; letter-spacing: 1px; }
.card-value { color: #ffffff; font-size: 1.8rem; font-weight: 800; margin-top: 4px; }
.card-sub   { color: #6b7280; font-size: 0.72rem; margin-top: 2px; }
.alert-box {
    background: linear-gradient(135deg, #3b0a0a, #1f0505);
    border: 1px solid #ef4444;
    border-radius: 10px;
    padding: 12px 16px;
    margin: 4px 0;
    color: #fca5a5;
    font-size: 0.85rem;
}
.alert-title { color: #f87171; font-weight: 700; font-size: 0.9rem; margin-bottom: 4px; }
.normal-box {
    background: linear-gradient(135deg, #052e16, #0a1a0e);
    border: 1px solid #22c55e;
    border-radius: 10px;
    padding: 10px 16px;
    color: #86efac;
    font-size: 0.82rem;
}
</style>
""", unsafe_allow_html=True)

INTERSECTION_COLORS = {
    "North Gate":    "#4ade80",
    "South Gate":    "#60a5fa",
    "East Junction": "#f472b6",
    "West Junction": "#fb923c",
    "City Center":   "#a78bfa",
}

# ── Load & cache data + model ──────────────────────────────────────────────────
@st.cache_data
def load_data():
    os.makedirs("data", exist_ok=True)
    if os.path.exists("data/sensor_data.csv"):
        df = pd.read_csv("data/sensor_data.csv", parse_dates=["timestamp"])
    else:
        df = generate_sensor_data()
    return df

@st.cache_resource
def load_model(degree):
    df = load_data()
    pipeline, metrics, y_true, y_pred = train_poly_model(df, degree=degree)
    return pipeline, metrics, y_true, y_pred

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚦 Controls")
    st.divider()

    selected_intersection = st.selectbox("📍 Intersection", ["All"] + INTERSECTIONS)

    st.markdown("**🕐 Hour Filter**")
    hour_range = st.slider("Hour of Day", 0, 23, (6, 22))

    st.markdown("**📅 Day Type**")
    day_type = st.radio("", ["All", "Weekdays", "Weekends"], index=0, label_visibility="collapsed")

    st.divider()
    st.markdown("**🔬 Model Settings**")
    poly_degree = st.selectbox("Polynomial Degree", [2, 3, 4], index=1)
    anomaly_threshold = st.slider("Anomaly Z-score Threshold", 1.5, 5.0, 3.0, step=0.5)
    anomaly_window = st.slider("Rolling Window (readings)", 5, 30, 12)

    st.divider()
    st.markdown("**⚡ Live Simulation**")
    live_mode = st.toggle("Enable Real-Time Mode", value=False)
    if live_mode:
        refresh_speed = st.slider("Refresh interval (sec)", 1, 5, 2)

    st.divider()
    st.markdown("**🔧 Manual Predict**")
    manual_count   = st.number_input("Vehicle Count", 0, 500, 120)
    manual_hour    = st.slider("Hour", 0, 23, 8)
    manual_weekend = st.checkbox("Is Weekend?", value=False)

# ── Load data & model ──────────────────────────────────────────────────────────
df_raw = load_data()
pipeline, metrics, y_true, y_pred = load_model(poly_degree)

# ── Filter ─────────────────────────────────────────────────────────────────────
df = df_raw.copy()
if selected_intersection != "All":
    df = df[df["intersection"] == selected_intersection]
df = df[(df["hour"] >= hour_range[0]) & (df["hour"] <= hour_range[1])]
if day_type == "Weekdays":
    df = df[df["is_weekend"] == 0]
elif day_type == "Weekends":
    df = df[df["is_weekend"] == 1]

# Predict light duration for filtered data
df = df.copy()
df["predicted_duration"] = pipeline.predict(build_features(df)).clip(5, 90)

# Anomaly detection per intersection
df["is_anomaly_detected"] = False
df["z_score"] = 0.0
for intr in df["intersection"].unique():
    mask = df["intersection"] == intr
    s = df.loc[mask, "vehicle_count"]
    flags, zscores = detect_anomalies(s, window=anomaly_window, threshold=anomaly_threshold)
    df.loc[mask, "is_anomaly_detected"] = flags.values
    df.loc[mask, "z_score"] = zscores.values

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🚦 Traffic Light Usage Optimizer")
st.caption("Polynomial Regression · Sensor Vehicle Counts · Anomaly Detection")
st.divider()

# ── KPI Cards ──────────────────────────────────────────────────────────────────
total_readings = len(df)
avg_count      = df["vehicle_count"].mean()
avg_duration   = df["predicted_duration"].mean()
anomaly_count  = df["is_anomaly_detected"].sum()

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="card">
        <div class="card-label">Total Readings</div>
        <div class="card-value">{total_readings:,}</div>
        <div class="card-sub">sensor records</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="card">
        <div class="card-label">Avg Vehicle Count</div>
        <div class="card-value">{avg_count:.0f}</div>
        <div class="card-sub">vehicles / reading</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="card">
        <div class="card-label">Avg Green Duration</div>
        <div class="card-value">{avg_duration:.1f}s</div>
        <div class="card-sub">predicted by model</div>
    </div>""", unsafe_allow_html=True)
with c4:
    color = "#ef4444" if anomaly_count > 0 else "#4ade80"
    st.markdown(f"""<div class="card">
        <div class="card-label">Anomalies Detected</div>
        <div class="card-value" style="color:{color}">{anomaly_count}</div>
        <div class="card-sub">z-score > {anomaly_threshold}</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# ── Manual Prediction ──────────────────────────────────────────────────────────
manual_pred = predict_light(pipeline, manual_count, manual_hour, int(manual_weekend))
intensity   = min(manual_count / 300, 1.0)
r = int(255 * intensity)
g = int(255 * (1 - intensity * 0.5))
light_color = f"rgb({r},{g},0)"
pct = (manual_pred - 5) / 85 * 100

st.markdown("### 🔧 Manual Prediction")
mcol1, mcol2 = st.columns([1, 2])
with mcol1:
    fig_manual = go.Figure(go.Indicator(
        mode="gauge+number",
        value=manual_pred,
        number={"suffix": "s", "font": {"size": 42, "color": "#ffffff"}},
        title={"text": f"Green Light Duration<br><span style='font-size:0.8em;color:#86efac'>{manual_count} vehicles · Hour {manual_hour}</span>",
               "font": {"color": "#86efac", "size": 14}},
        gauge={
            "axis": {"range": [0, 90], "tickcolor": "#374151"},
            "bar":  {"color": light_color, "thickness": 0.3},
            "bgcolor": "#111827",
            "bordercolor": "#1f2937",
            "steps": [
                {"range": [0,  30], "color": "#052e16"},
                {"range": [30, 60], "color": "#14532d"},
                {"range": [60, 90], "color": "#166534"},
            ],
            "threshold": {"line": {"color": "#fbbf24", "width": 3},
                          "thickness": 0.8, "value": 45},
        },
    ))
    fig_manual.update_layout(
        paper_bgcolor="#0b0f1a", height=280,
        margin=dict(l=20, r=20, t=50, b=10),
    )
    st.plotly_chart(fig_manual, use_container_width=True)

with mcol2:
    st.markdown(f"""
    **Input Summary**
    | Parameter | Value |
    |-----------|-------|
    | Vehicle Count | {manual_count} |
    | Hour | {manual_hour}:00 |
    | Weekend | {'Yes' if manual_weekend else 'No'} |
    | **Predicted Green** | **{manual_pred:.1f} seconds** |
    | Signal Intensity | {pct:.0f}% |
    """)
    if manual_pred > 70:
        st.error("🔴 Heavy traffic — maximum green time allocated.")
    elif manual_pred > 45:
        st.warning("🟡 Moderate traffic — extended green phase.")
    else:
        st.success("🟢 Light traffic — short green phase.")

st.divider()

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Real-Time Bar Chart",
    "📈 Regression Curve",
    "🚨 Anomaly Monitor",
    "🏙️ Intersection Comparison",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — REAL-TIME BAR CHART
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Live Vehicle Count & Predicted Green Duration")

    chart_placeholder  = st.empty()
    alert_placeholder  = st.empty()
    status_placeholder = st.empty()

    def render_bar_chart(snapshot_df):
        bar_df = (
            snapshot_df.groupby("intersection")
            .agg(
                vehicle_count    =("vehicle_count",     "mean"),
                predicted_duration=("predicted_duration","mean"),
                anomaly_count    =("is_anomaly_detected","sum"),
            )
            .reset_index()
            .sort_values("vehicle_count", ascending=False)
        )

        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("🚗 Avg Vehicle Count per Intersection",
                            "🟢 Predicted Green Duration (seconds)"),
            horizontal_spacing=0.12,
        )

        colors_bar = [INTERSECTION_COLORS.get(i, "#60a5fa") for i in bar_df["intersection"]]
        anomaly_flags = bar_df["anomaly_count"] > 0
        bar_colors_v = ["#ef4444" if a else c for a, c in zip(anomaly_flags, colors_bar)]

        fig.add_trace(go.Bar(
            x=bar_df["intersection"],
            y=bar_df["vehicle_count"],
            marker_color=bar_colors_v,
            text=bar_df["vehicle_count"].round(0).astype(int),
            textposition="outside",
            name="Vehicle Count",
            showlegend=False,
        ), row=1, col=1)

        duration_colors = []
        for d in bar_df["predicted_duration"]:
            if d > 70:   duration_colors.append("#ef4444")
            elif d > 45: duration_colors.append("#fbbf24")
            else:        duration_colors.append("#4ade80")

        fig.add_trace(go.Bar(
            x=bar_df["intersection"],
            y=bar_df["predicted_duration"],
            marker_color=duration_colors,
            text=bar_df["predicted_duration"].round(1).astype(str) + "s",
            textposition="outside",
            name="Green Duration",
            showlegend=False,
        ), row=1, col=2)

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0b0f1a",
            plot_bgcolor="#0d1b2a",
            height=420,
            margin=dict(l=20, r=20, t=60, b=60),
            font=dict(color="#e2e8f0"),
        )
        fig.update_yaxes(gridcolor="#1f2937")
        fig.update_xaxes(tickangle=-15)
        return fig, bar_df

    def render_alerts(snapshot_df):
        alerts = snapshot_df[snapshot_df["is_anomaly_detected"]]
        if len(alerts) == 0:
            return '<div class="normal-box">✅ All intersections operating normally — no anomalies detected.</div>'
        html = ""
        for intr, grp in alerts.groupby("intersection"):
            worst_z = grp["z_score"].abs().max()
            worst_v = grp.loc[grp["z_score"].abs().idxmax(), "vehicle_count"]
            html += f"""<div class="alert-box">
                <div class="alert-title">🚨 ANOMALY — {intr}</div>
                {len(grp)} anomalous readings &nbsp;|&nbsp;
                Peak count: <b>{worst_v}</b> vehicles &nbsp;|&nbsp;
                Max Z-score: <b>{worst_z:.2f}</b>
            </div>"""
        return html

    # ── Live mode ──────────────────────────────────────────────────────────────
    if live_mode:
        unique_times = df["timestamp"].sort_values().unique()
        step = max(1, len(unique_times) // 100)
        sampled_times = unique_times[::step]

        for i, ts in enumerate(sampled_times):
            window_df = df[df["timestamp"] <= ts].tail(500)
            fig_bar, bar_summary = render_bar_chart(window_df)

            with chart_placeholder.container():
                st.markdown(f"**🕐 Simulated time: `{pd.Timestamp(ts).strftime('%Y-%m-%d %H:%M')}`** &nbsp; Reading {i+1}/{len(sampled_times)}")
                st.plotly_chart(fig_bar, use_container_width=True)

            alert_placeholder.markdown(render_alerts(window_df), unsafe_allow_html=True)
            time.sleep(refresh_speed)
    else:
        # Static snapshot — last 2 hours of data
        latest = df["timestamp"].max()
        snapshot = df[df["timestamp"] >= latest - pd.Timedelta(hours=2)]
        if len(snapshot) == 0:
            snapshot = df.tail(500)

        fig_bar, bar_summary = render_bar_chart(snapshot)
        with chart_placeholder.container():
            st.markdown("**📸 Snapshot — last 2 hours of data** &nbsp; *(enable Real-Time Mode in sidebar for live updates)*")
            st.plotly_chart(fig_bar, use_container_width=True)

        alert_placeholder.markdown(render_alerts(snapshot), unsafe_allow_html=True)

        # Time-series line below bars
        st.markdown("#### Hourly Vehicle Count Trend")
        hourly = (
            df.groupby(["hour", "intersection"])["vehicle_count"]
            .mean().reset_index()
        )
        fig_line = px.line(
            hourly, x="hour", y="vehicle_count", color="intersection",
            color_discrete_map=INTERSECTION_COLORS,
            markers=True,
            labels={"vehicle_count": "Avg Vehicles", "hour": "Hour of Day"},
        )
        fig_line.update_layout(
            template="plotly_dark", paper_bgcolor="#0b0f1a", plot_bgcolor="#0d1b2a",
            height=350, margin=dict(l=30, r=20, t=20, b=40),
            legend=dict(orientation="h", y=-0.25),
        )
        st.plotly_chart(fig_line, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — REGRESSION CURVE
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader(f"Polynomial Regression (Degree {poly_degree})")
    st.markdown(f"**Model Metrics** &nbsp; MAE: `{metrics['MAE']}s` &nbsp; R²: `{metrics['R2']}`")

    # Scatter: actual vs predicted (sample for speed)
    sample = df.sample(min(3000, len(df)), random_state=0)
    sample_pred = pipeline.predict(build_features(sample)).clip(5, 90)

    v_range = np.linspace(0, df["vehicle_count"].max(), 300)

    fig_reg = go.Figure()

    # Scatter actual points
    anom_mask = sample["is_anomaly_detected"]
    fig_reg.add_trace(go.Scatter(
        x=sample.loc[~anom_mask, "vehicle_count"],
        y=vehicle_to_light_duration(sample.loc[~anom_mask, "vehicle_count"].values),
        mode="markers", name="Normal",
        marker=dict(color="#4ade80", size=4, opacity=0.4),
    ))
    fig_reg.add_trace(go.Scatter(
        x=sample.loc[anom_mask, "vehicle_count"],
        y=vehicle_to_light_duration(sample.loc[anom_mask, "vehicle_count"].values),
        mode="markers", name="Anomaly",
        marker=dict(color="#ef4444", size=6, symbol="x", opacity=0.7),
    ))

    # Polynomial curve — fix hour=8, weekday for clean curve
    curve_X = np.column_stack([v_range, np.full(300, 8), np.zeros(300)])
    curve_y = pipeline.predict(curve_X).clip(5, 90)
    fig_reg.add_trace(go.Scatter(
        x=v_range, y=curve_y,
        mode="lines", name=f"Poly Degree {poly_degree}",
        line=dict(color="#fbbf24", width=3),
    ))

    fig_reg.update_layout(
        template="plotly_dark", paper_bgcolor="#0b0f1a", plot_bgcolor="#0d1b2a",
        title="Vehicle Count → Predicted Green Light Duration",
        xaxis_title="Vehicle Count", yaxis_title="Green Duration (seconds)",
        height=460, margin=dict(l=40, r=20, t=60, b=40),
        legend=dict(orientation="h", y=-0.15),
    )
    st.plotly_chart(fig_reg, use_container_width=True)

    # Residuals
    with st.expander("🔍 Residual Plot"):
        residuals = y_true - y_pred
        fig_res = go.Figure()
        fig_res.add_trace(go.Scatter(
            x=y_pred, y=residuals, mode="markers",
            marker=dict(color="#60a5fa", size=3, opacity=0.4),
            name="Residuals",
        ))
        fig_res.add_hline(y=0, line_dash="dash", line_color="#6b7280")
        fig_res.update_layout(
            template="plotly_dark", paper_bgcolor="#0b0f1a",
            title="Residuals vs Fitted", height=320,
            xaxis_title="Fitted (s)", yaxis_title="Residual (s)",
            margin=dict(l=40, r=20, t=50, b=40),
        )
        st.plotly_chart(fig_res, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — ANOMALY MONITOR
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("🚨 Anomaly Detection Monitor")

    total_anom = df["is_anomaly_detected"].sum()
    anom_rate  = total_anom / len(df) * 100

    a1, a2, a3 = st.columns(3)
    a1.metric("Total Anomalies",  f"{total_anom:,}")
    a2.metric("Anomaly Rate",     f"{anom_rate:.2f}%")
    a3.metric("Clean Readings",   f"{len(df) - total_anom:,}")

    # Anomaly count per intersection
    anom_by_intr = df.groupby("intersection")["is_anomaly_detected"].sum().reset_index()
    anom_by_intr.columns = ["Intersection", "Anomalies"]

    fig_anom_bar = px.bar(
        anom_by_intr, x="Intersection", y="Anomalies",
        color="Intersection", color_discrete_map=INTERSECTION_COLORS,
        title="Anomaly Count by Intersection",
    )
    fig_anom_bar.update_layout(
        template="plotly_dark", paper_bgcolor="#0b0f1a",
        height=350, showlegend=False,
        margin=dict(l=30, r=20, t=50, b=40),
    )
    st.plotly_chart(fig_anom_bar, use_container_width=True)

    # Z-score time series
    st.markdown("#### Z-Score Time Series")
    sel_intr = st.selectbox("Select Intersection", INTERSECTIONS, key="anom_intr")
    intr_df  = df[df["intersection"] == sel_intr].sort_values("timestamp")

    fig_z = go.Figure()
    fig_z.add_trace(go.Scatter(
        x=intr_df["timestamp"], y=intr_df["z_score"],
        mode="lines", name="Z-Score",
        line=dict(color="#60a5fa", width=1),
    ))
    fig_z.add_hline(y=anomaly_threshold,  line_dash="dash", line_color="#ef4444",
                    annotation_text="Upper threshold")
    fig_z.add_hline(y=-anomaly_threshold, line_dash="dash", line_color="#ef4444",
                    annotation_text="Lower threshold")

    # Mark anomaly points
    anom_pts = intr_df[intr_df["is_anomaly_detected"]]
    fig_z.add_trace(go.Scatter(
        x=anom_pts["timestamp"], y=anom_pts["z_score"],
        mode="markers", name="Anomaly",
        marker=dict(color="#ef4444", size=7, symbol="x"),
    ))

    fig_z.update_layout(
        template="plotly_dark", paper_bgcolor="#0b0f1a", plot_bgcolor="#0d1b2a",
        height=380, margin=dict(l=30, r=20, t=20, b=40),
        legend=dict(orientation="h", y=-0.2),
        xaxis_title="Time", yaxis_title="Z-Score",
    )
    st.plotly_chart(fig_z, use_container_width=True)

    # Anomaly table
    with st.expander("📋 Anomaly Records Table"):
        anom_records = df[df["is_anomaly_detected"]][
            ["timestamp", "intersection", "vehicle_count", "predicted_duration", "z_score"]
        ].sort_values("z_score", ascending=False).head(100)
        anom_records["z_score"] = anom_records["z_score"].round(2)
        anom_records["predicted_duration"] = anom_records["predicted_duration"].round(1)
        st.dataframe(anom_records, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — INTERSECTION COMPARISON
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("🏙️ Intersection-Level Comparison")

    # Heatmap: intersection × hour
    pivot = (
        df.groupby(["intersection", "hour"])["vehicle_count"]
        .mean().reset_index()
        .pivot(index="intersection", columns="hour", values="vehicle_count")
    )
    fig_hm = px.imshow(
        pivot, color_continuous_scale="Greens",
        title="Avg Vehicle Count — Intersection × Hour",
        aspect="auto",
        labels=dict(x="Hour of Day", y="Intersection", color="Avg Vehicles"),
    )
    fig_hm.update_layout(
        template="plotly_dark", paper_bgcolor="#0b0f1a",
        height=360, margin=dict(l=20, r=20, t=50, b=40),
    )
    st.plotly_chart(fig_hm, use_container_width=True)

    # Box plot distribution
    fig_box = px.box(
        df, x="intersection", y="vehicle_count",
        color="intersection", color_discrete_map=INTERSECTION_COLORS,
        title="Vehicle Count Distribution by Intersection",
        points="outliers",
    )
    fig_box.update_layout(
        template="plotly_dark", paper_bgcolor="#0b0f1a",
        height=380, showlegend=False,
        margin=dict(l=30, r=20, t=50, b=40),
    )
    st.plotly_chart(fig_box, use_container_width=True)

    # Summary stats table
    st.markdown("#### Summary Statistics")
    summary = (
        df.groupby("intersection")
        .agg(
            avg_vehicles    =("vehicle_count",      "mean"),
            max_vehicles    =("vehicle_count",      "max"),
            avg_green_sec   =("predicted_duration", "mean"),
            total_anomalies =("is_anomaly_detected","sum"),
        )
        .round(1)
        .reset_index()
    )
    summary.columns = ["Intersection", "Avg Vehicles", "Peak Vehicles", "Avg Green (s)", "Anomalies"]
    st.dataframe(summary, use_container_width=True, hide_index=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<center><small>🚦 Traffic Light Optimizer · Polynomial Regression · Streamlit + Plotly</small></center>",
    unsafe_allow_html=True,
)
