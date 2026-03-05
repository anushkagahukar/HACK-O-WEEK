"""
app.py
------
Streamlit dashboard for Time-Series Usage Analysis and Forecast.

Sections:
  1. Sidebar  – file upload + forecast controls
  2. Overview – KPI metrics + raw data preview
  3. Historical Visualization
  4. Prophet Forecast + What-If Scenario Tool
  5. Naive Bayes Category Predictor
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import timedelta

# Local module
from model import (
    generate_sample_data,
    load_and_validate,
    UsageClassifier,
    UsageForecaster,
)

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Usage Analysis & Forecast",
    page_icon="📈",
    layout="wide",
)

# ── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    .metric-card {
        background: #1e1e2e;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin-bottom: 0.5rem;
    }
    h1 { color: #c9d1d9; }
    .stSlider > div { padding-top: 0.3rem; }
</style>
""", unsafe_allow_html=True)

# ── TITLE ────────────────────────────────────────────────────────────────────
st.title("📈 Time-Series Usage Analysis & Forecast Dashboard")
st.caption("Powered by Prophet · Gaussian Naive Bayes · Streamlit")
st.divider()


# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Controls")

    uploaded_file = st.file_uploader(
        "Upload CSV (date, usage, category)",
        type=["csv"],
        help="Leave empty to use the built-in sample dataset.",
    )

    st.subheader("Forecast Settings")
    forecast_days = st.slider(
        "Forecast horizon (days)", min_value=7, max_value=90, value=30, step=1
    )

    st.subheader("About")
    st.info(
        "Upload your own CSV or explore the auto-generated sample dataset. "
        "Adjust controls to update forecasts and predictions in real time."
    )


# ── DATA LOADING ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading data …")
def get_data(file) -> pd.DataFrame:
    if file is not None:
        df = load_and_validate(file)
    else:
        df = generate_sample_data()
        df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)


df = get_data(uploaded_file)

data_source = "📂 Uploaded file" if uploaded_file else "🔧 Auto-generated sample"
st.caption(f"Data source: **{data_source}** · {len(df):,} rows")


# ── SECTION 1 – KPI METRICS + DATA PREVIEW ───────────────────────────────────
st.subheader("📊 Dataset Overview")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Records", f"{len(df):,}")
col2.metric("Avg Daily Usage", f"{df['usage'].mean():.1f}")
col3.metric("Peak Usage", f"{df['usage'].max():.1f}")
col4.metric("Date Range", f"{(df['date'].max() - df['date'].min()).days} days")

with st.expander("🔍 Preview raw data", expanded=False):
    st.dataframe(df.head(50), use_container_width=True)
    st.caption(f"Showing first 50 of {len(df)} rows.")

st.divider()


# ── SECTION 2 – HISTORICAL USAGE CHART ───────────────────────────────────────
st.subheader("📉 Historical Usage")

category_colors = {"Low": "#4CAF50", "Medium": "#FF9800", "High": "#F44336"}

fig_hist = go.Figure()

# Shaded band: rolling mean ± std for context
rolling = df.set_index("date")["usage"].rolling(7)
df_roll = df.copy()
df_roll["roll_mean"] = rolling.mean().values
df_roll["roll_std"] = rolling.std().values

fig_hist.add_trace(go.Scatter(
    x=pd.concat([df_roll["date"], df_roll["date"].iloc[::-1]]),
    y=pd.concat([
        df_roll["roll_mean"] + df_roll["roll_std"],
        (df_roll["roll_mean"] - df_roll["roll_std"]).iloc[::-1],
    ]),
    fill="toself",
    fillcolor="rgba(99,179,237,0.15)",
    line=dict(color="rgba(0,0,0,0)"),
    name="±1 σ band (7-day)",
    showlegend=True,
))

# Line: raw usage
fig_hist.add_trace(go.Scatter(
    x=df["date"], y=df["usage"],
    mode="lines",
    line=dict(color="#63B3ED", width=1.5),
    name="Usage",
))

# 7-day rolling mean
fig_hist.add_trace(go.Scatter(
    x=df_roll["date"], y=df_roll["roll_mean"],
    mode="lines",
    line=dict(color="#F6AD55", width=2, dash="dot"),
    name="7-day avg",
))

fig_hist.update_layout(
    height=360,
    xaxis_title="Date", yaxis_title="Usage",
    legend=dict(orientation="h", y=1.05),
    margin=dict(l=0, r=0, t=20, b=0),
    plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
    font=dict(color="#c9d1d9"),
    xaxis=dict(gridcolor="#1e1e2e"),
    yaxis=dict(gridcolor="#1e1e2e"),
)
st.plotly_chart(fig_hist, use_container_width=True)

# Category distribution pie
col_a, col_b = st.columns([1, 2])
with col_a:
    cat_counts = df["category"].value_counts().reset_index()
    cat_counts.columns = ["Category", "Count"]
    fig_pie = px.pie(
        cat_counts, names="Category", values="Count",
        color="Category",
        color_discrete_map=category_colors,
        hole=0.45,
        title="Category Distribution",
    )
    fig_pie.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=40, b=0),
        plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
        font=dict(color="#c9d1d9"),
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_b:
    # Weekly heatmap – avg usage by day-of-week & month
    df_heat = df.copy()
    df_heat["dow"] = df_heat["date"].dt.day_name()
    df_heat["month"] = df_heat["date"].dt.strftime("%b %Y")
    pivot = df_heat.pivot_table(
        index="dow", columns="month", values="usage", aggfunc="mean"
    )
    dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    pivot = pivot.reindex([d for d in dow_order if d in pivot.index])

    fig_heat = px.imshow(
        pivot,
        color_continuous_scale="Blues",
        title="Avg Usage Heat-map (Day × Month)",
        aspect="auto",
    )
    fig_heat.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=40, b=0),
        plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
        font=dict(color="#c9d1d9"),
        coloraxis_colorbar=dict(title="Avg"),
    )
    st.plotly_chart(fig_heat, use_container_width=True)

st.divider()


# ── SECTION 3 – PROPHET FORECAST ─────────────────────────────────────────────
st.subheader(f"🔮 Prophet Forecast — next {forecast_days} days")

@st.cache_data(show_spinner="Training Prophet model …")
def run_forecast(df_hash: str, periods: int, _df: pd.DataFrame):
    """Cache key includes a df hash so re-uploads retrigger training."""
    forecaster = UsageForecaster()
    forecast = forecaster.fit_and_forecast(_df, periods=periods)
    return forecaster, forecast

# Build a lightweight hash for cache invalidation
df_hash = str(df["usage"].sum()) + str(len(df)) + str(forecast_days)
forecaster, forecast = run_forecast(df_hash, forecast_days, df)

# Split into historical fitted vs future
last_hist_date = df["date"].max()
fc_future = forecast[forecast["ds"] > last_hist_date]
fc_hist   = forecast[forecast["ds"] <= last_hist_date]

fig_fc = go.Figure()

# Confidence interval ribbon (future)
fig_fc.add_trace(go.Scatter(
    x=pd.concat([fc_future["ds"], fc_future["ds"].iloc[::-1]]),
    y=pd.concat([fc_future["yhat_upper"], fc_future["yhat_lower"].iloc[::-1]]),
    fill="toself",
    fillcolor="rgba(167,139,250,0.20)",
    line=dict(color="rgba(0,0,0,0)"),
    name="95 % CI (future)",
))

# Historical actuals
fig_fc.add_trace(go.Scatter(
    x=df["date"], y=df["usage"],
    mode="lines",
    line=dict(color="#63B3ED", width=1.2),
    name="Actual",
))

# Prophet fitted line (historical)
fig_fc.add_trace(go.Scatter(
    x=fc_hist["ds"], y=fc_hist["yhat"],
    mode="lines",
    line=dict(color="#F6AD55", width=1.5, dash="dot"),
    name="Fitted",
))

# Prophet forecast line (future)
fig_fc.add_trace(go.Scatter(
    x=fc_future["ds"], y=fc_future["yhat"],
    mode="lines",
    line=dict(color="#A78BFA", width=2.5),
    name="Forecast",
))

# Vertical separator
fig_fc.add_vline(
    x=last_hist_date.timestamp() * 1000,
    line_dash="dash", line_color="#718096",
    annotation_text="Forecast Start",
    annotation_position="top left",
)

fig_fc.update_layout(
    height=420,
    xaxis_title="Date", yaxis_title="Usage",
    legend=dict(orientation="h", y=1.06),
    margin=dict(l=0, r=0, t=20, b=0),
    plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
    font=dict(color="#c9d1d9"),
    xaxis=dict(gridcolor="#1e1e2e"),
    yaxis=dict(gridcolor="#1e1e2e"),
)
st.plotly_chart(fig_fc, use_container_width=True)

# Forecast summary table
with st.expander("📋 Forecast Data Table", expanded=False):
    fc_display = fc_future[["ds","yhat","yhat_lower","yhat_upper"]].copy()
    fc_display.columns = ["Date","Predicted","Lower CI","Upper CI"]
    fc_display = fc_display.round(2)
    st.dataframe(fc_display, use_container_width=True)

st.divider()


# ── SECTION 4 – WHAT-IF SCENARIO TOOL ───────────────────────────────────────
st.subheader("🎯 What-If Scenario Tool")
st.caption("Move the slider to a future day and see the predicted usage.")

future_dates = fc_future["ds"].dt.date.tolist()

if future_dates:
    selected_day_idx = st.slider(
        "Select future day",
        min_value=0,
        max_value=len(future_dates) - 1,
        value=0,
        format="",
        key="scenario_slider",
    )
    selected_date = pd.Timestamp(future_dates[selected_day_idx])
    result = forecaster.get_future_value(selected_date)

    if result:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📅 Date", selected_date.strftime("%d %b %Y"))
        c2.metric("📌 Predicted Usage", f"{result['yhat']:.1f}")
        c3.metric("⬇️ Lower Bound (95%)", f"{result['yhat_lower']:.1f}")
        c4.metric("⬆️ Upper Bound (95%)", f"{result['yhat_upper']:.1f}")
else:
    st.warning("No future forecast dates available — increase forecast horizon.")

st.divider()


# ── SECTION 5 – NAIVE BAYES CLASSIFIER ──────────────────────────────────────
st.subheader("🤖 Naive Bayes Usage Category Predictor")

@st.cache_resource(show_spinner="Training Naive Bayes …")
def train_classifier(df_hash: str, _df: pd.DataFrame) -> UsageClassifier:
    clf = UsageClassifier()
    clf.train(_df)
    return clf

clf_hash = str(len(df)) + str(df["usage"].sum())
classifier = train_classifier(clf_hash, df)

col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown("**Model Accuracy**")
    st.metric("Test Accuracy", f"{classifier.accuracy * 100:.1f} %")

    st.markdown("**Classification Report**")
    report_df = pd.DataFrame(classifier.report).T.round(3)
    st.dataframe(report_df, use_container_width=True)

with col_right:
    st.markdown("**Interactive Prediction**")
    usage_min = float(df["usage"].min())
    usage_max = float(df["usage"].max())
    usage_mean = float(df["usage"].mean())

    user_usage = st.slider(
        "Enter a usage value:",
        min_value=round(usage_min - 20, 0),
        max_value=round(usage_max + 20, 0),
        value=round(usage_mean, 0),
        step=1.0,
        key="nb_slider",
    )

    predicted_cat = classifier.predict(user_usage)
    probabilities = classifier.predict_proba(user_usage)

    cat_emoji = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}
    st.markdown(
        f"### Predicted Category: {cat_emoji.get(predicted_cat, '⚪')} **{predicted_cat}**"
    )

    st.markdown("**Class Probabilities**")
    prob_df = pd.DataFrame(
        list(probabilities.items()), columns=["Category", "Probability"]
    ).sort_values("Probability", ascending=False)

    fig_bar = px.bar(
        prob_df, x="Category", y="Probability",
        color="Category",
        color_discrete_map={"Low": "#4CAF50", "Medium": "#FF9800", "High": "#F44336"},
        range_y=[0, 1],
        text_auto=".2%",
    )
    fig_bar.update_layout(
        height=260,
        showlegend=False,
        margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
        font=dict(color="#c9d1d9"),
        xaxis=dict(gridcolor="#1e1e2e"),
        yaxis=dict(gridcolor="#1e1e2e"),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()
st.caption("Built with ❤️ using Streamlit · Prophet · Scikit-learn · Plotly")
