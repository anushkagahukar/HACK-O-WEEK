"""
app.py
------
Streamlit dashboard for Cooling Demand Prediction.

Sections:
  1. Dataset Preview
  2. Cooling Prediction (interactive sliders)
  3. Zone Heatmap
"""

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from model import generate_data, train_model, predict

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cooling Demand Prediction",
    page_icon="❄️",
    layout="wide",
)

# ── HEADER ────────────────────────────────────────────────────────────────────
st.title("❄️ Cooling Demand Prediction")
st.caption("Decision Tree Classifier · Occupancy & Temperature Data")
st.divider()

# ── LOAD DATA & TRAIN MODEL ───────────────────────────────────────────────────
@st.cache_resource
def setup():
    """Load (or generate) data and train the model once."""
    uploaded = st.session_state.get("uploaded_df")
    df = uploaded if uploaded is not None else generate_data()
    model, accuracy = train_model(df)
    return df, model, accuracy

# File upload in sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    file = st.file_uploader("Upload CSV (optional)", type=["csv"])
    if file:
        try:
            st.session_state["uploaded_df"] = pd.read_csv(file)
            st.success("File loaded!")
        except Exception as e:
            st.error(f"Error: {e}")

    st.info("No file? A synthetic 100-row dataset is used automatically.")

df, model, accuracy = setup()

# ── SECTION 1 – DATASET PREVIEW ──────────────────────────────────────────────
st.subheader("📋 Section 1 — Dataset Preview")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Rows", len(df))
col2.metric("Model Accuracy", f"{accuracy} %")
col3.metric("Cooling Required", int(df["cooling_needed"].sum()))
col4.metric("Not Required", int((df["cooling_needed"] == 0).sum()))

st.dataframe(df, use_container_width=True, height=220)
st.divider()

# ── SECTION 2 – COOLING PREDICTION ───────────────────────────────────────────
st.subheader("🎛️ Section 2 — Cooling Prediction")
st.caption("Adjust the sliders and get an instant prediction.")

c1, c2, c3 = st.columns(3)
with c1:
    temp = st.slider("🌡️ Temperature (°C)", 18, 38, 28)
with c2:
    occ  = st.slider("👥 Occupancy (people)", 1, 30, 12)
with c3:
    hum  = st.slider("💧 Humidity (%)", 30, 85, 55)

result = predict(model, temp, occ, hum)

st.markdown("### Prediction Result")
if result == 1:
    st.success("✅ **Cooling Required** — Conditions exceed comfort thresholds.")
else:
    st.info("🔵 **Cooling Not Required** — Conditions are within comfortable range.")

# Display input summary
with st.expander("Input Summary"):
    st.write(pd.DataFrame(
        {"Temperature (°C)": [temp], "Occupancy": [occ], "Humidity (%)": [hum]}
    ))

st.divider()

# ── SECTION 3 – ZONE HEATMAP ──────────────────────────────────────────────────
st.subheader("🗺️ Section 3 — Zone Cooling Demand Heatmap")
st.caption("Average cooling demand intensity per zone across key features.")

# Build pivot: zones × features (mean values where cooling_needed=1)
zone_stats = (
    df.groupby("zone")[["temperature", "occupancy", "humidity", "cooling_needed"]]
    .mean()
    .round(1)
)

col_map, col_table = st.columns([2, 1])

with col_map:
    fig, ax = plt.subplots(figsize=(7, 3.5))
    sns.heatmap(
        zone_stats,
        annot=True,
        fmt=".1f",
        cmap="YlOrRd",
        linewidths=0.5,
        linecolor="#333",
        ax=ax,
        cbar_kws={"shrink": 0.8},
    )
    ax.set_title("Zone vs Feature Intensity", fontsize=13, pad=10)
    ax.set_xlabel("")
    ax.set_ylabel("Zone", fontsize=11)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    st.pyplot(fig)

with col_table:
    st.markdown("**Zone Averages**")
    st.dataframe(zone_stats, use_container_width=True)

st.divider()
st.caption("Built with ❤️ using Streamlit · Scikit-learn · Seaborn")
