"""
poly_model.py — Polynomial Regression: vehicle count → light usage duration
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, r2_score


def vehicle_to_light_duration(vehicle_count: np.ndarray) -> np.ndarray:
    """
    Ground-truth formula (simulated):
    Light green duration (seconds) is a nonlinear function of vehicle count.
    Low count  → short green (5-15s)
    High count → longer green (up to 90s), with saturation
    """
    v = np.array(vehicle_count, dtype=float)
    duration = (
        5
        + 0.35  * v
        - 0.0008 * v ** 2
        + 0.000001 * v ** 3
        + np.random.normal(0, 2, size=len(v))
    )
    return np.clip(duration, 5, 90)


def build_features(df: pd.DataFrame) -> np.ndarray:
    """Extract features: vehicle_count, hour, is_weekend."""
    return df[["vehicle_count", "hour", "is_weekend"]].values


def train_poly_model(df: pd.DataFrame, degree: int = 3):
    """Train polynomial regression pipeline."""
    X = build_features(df)
    y = vehicle_to_light_duration(df["vehicle_count"].values)

    pipeline = Pipeline([
        ("poly",   PolynomialFeatures(degree=degree, include_bias=False)),
        ("scaler", StandardScaler()),
        ("reg",    LinearRegression()),
    ])
    pipeline.fit(X, y)

    y_pred = pipeline.predict(X)
    metrics = {
        "MAE":  round(mean_absolute_error(y, y_pred), 3),
        "R2":   round(r2_score(y, y_pred), 4),
        "degree": degree,
    }
    return pipeline, metrics, y, y_pred


def predict_light(pipeline, vehicle_count: int, hour: int, is_weekend: int) -> float:
    X = np.array([[vehicle_count, hour, is_weekend]])
    pred = pipeline.predict(X)[0]
    return float(np.clip(pred, 5, 90))


def detect_anomalies(series: pd.Series, window: int = 12, threshold: float = 3.0):
    """
    Rolling Z-score anomaly detection on vehicle count.
    Returns boolean Series — True = anomaly.
    """
    rolling_mean = series.rolling(window=window, min_periods=1).mean()
    rolling_std  = series.rolling(window=window, min_periods=1).std().fillna(1)
    z_scores     = (series - rolling_mean) / rolling_std
    return z_scores.abs() > threshold, z_scores
