"""
model.py
--------
Contains all ML logic:
  - Data loading / generation
  - Naive Bayes classification (GaussianNB)
  - Prophet time-series forecasting
"""

import numpy as np
import pandas as pd
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# ── Prophet import (suppress noisy Stan / cmdstan output) ───────────────────
import logging
logging.getLogger("prophet").setLevel(logging.ERROR)
logging.getLogger("cmdstanpy").setLevel(logging.ERROR)
from prophet import Prophet


# ── 1. DATA UTILITIES ────────────────────────────────────────────────────────

def generate_sample_data(n_days: int = 365) -> pd.DataFrame:
    """
    Generate synthetic daily usage data with trend, weekly seasonality,
    and Gaussian noise.  Categories are derived from usage thresholds.
    """
    np.random.seed(42)
    dates = pd.date_range(start="2023-01-01", periods=n_days, freq="D")
    trend = np.linspace(100, 200, n_days)
    seasonality = 30 * np.sin(2 * np.pi * np.arange(n_days) / 7)
    noise = np.random.normal(0, 10, n_days)
    usage = trend + seasonality + noise

    df = pd.DataFrame({
        "date": dates.strftime("%Y-%m-%d"),
        "usage": np.round(usage, 2),
        "category": [_categorize(u) for u in usage],
    })
    return df


def _categorize(value: float) -> str:
    """Map a usage value to a Low / Medium / High label."""
    if value < 130:
        return "Low"
    elif value < 170:
        return "Medium"
    else:
        return "High"


def load_and_validate(uploaded_file) -> pd.DataFrame:
    """
    Read a user-uploaded CSV.  Validates that the required columns exist
    and coerces types.  Returns a clean DataFrame.
    """
    df = pd.read_csv(uploaded_file)
    required = {"date", "usage", "category"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing columns: {missing}")

    df["date"] = pd.to_datetime(df["date"])
    df["usage"] = pd.to_numeric(df["usage"], errors="coerce")
    df = df.dropna(subset=["date", "usage"])

    # Ensure categories are title-cased
    df["category"] = df["category"].str.strip().str.title()
    return df


# ── 2. NAIVE BAYES CLASSIFIER ────────────────────────────────────────────────

class UsageClassifier:
    """
    Gaussian Naive Bayes wrapper that classifies a raw usage value
    into Low / Medium / High.
    """

    def __init__(self):
        self.model = GaussianNB()
        self.encoder = LabelEncoder()
        self.is_trained = False
        self.accuracy = None
        self.report = None

    def train(self, df: pd.DataFrame) -> None:
        """Fit the model on the usage column and category labels."""
        X = df[["usage"]].values
        y = self.encoder.fit_transform(df["category"])

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)

        self.accuracy = accuracy_score(y_test, y_pred)
        self.report = classification_report(
            y_test, y_pred,
            target_names=self.encoder.classes_,
            output_dict=True,
        )
        self.is_trained = True

    def predict(self, usage_value: float) -> str:
        """Return the predicted category string for a single usage value."""
        if not self.is_trained:
            raise RuntimeError("Model has not been trained yet.")
        X = np.array([[usage_value]])
        label_idx = self.model.predict(X)[0]
        return self.encoder.inverse_transform([label_idx])[0]

    def predict_proba(self, usage_value: float) -> dict:
        """Return a dict of {class: probability} for a single usage value."""
        if not self.is_trained:
            raise RuntimeError("Model has not been trained yet.")
        X = np.array([[usage_value]])
        probs = self.model.predict_proba(X)[0]
        return dict(zip(self.encoder.classes_, np.round(probs, 3)))


# ── 3. PROPHET FORECASTER ────────────────────────────────────────────────────

class UsageForecaster:
    """
    Thin wrapper around Facebook Prophet for daily usage forecasting.
    """

    def __init__(self):
        self.model = None
        self.forecast = None

    def fit_and_forecast(self, df: pd.DataFrame, periods: int = 30) -> pd.DataFrame:
        """
        Train Prophet on historical data and return a forecast DataFrame.

        Parameters
        ----------
        df      : DataFrame with columns 'date' and 'usage'
        periods : Number of future days to predict

        Returns
        -------
        forecast DataFrame containing ds, yhat, yhat_lower, yhat_upper
        """
        # Prophet requires columns named 'ds' and 'y'
        prophet_df = df[["date", "usage"]].rename(
            columns={"date": "ds", "usage": "y"}
        )
        prophet_df["ds"] = pd.to_datetime(prophet_df["ds"])

        self.model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=True,
            interval_width=0.95,         # 95 % confidence intervals
        )
        self.model.fit(prophet_df)

        future = self.model.make_future_dataframe(periods=periods, freq="D")
        self.forecast = self.model.predict(future)
        return self.forecast

    def get_future_value(self, target_date: pd.Timestamp) -> dict:
        """
        Look up the forecasted value (and CI) for a specific future date.
        Returns a dict with yhat, yhat_lower, yhat_upper.
        """
        if self.forecast is None:
            raise RuntimeError("Forecast has not been generated yet.")
        row = self.forecast[self.forecast["ds"] == target_date]
        if row.empty:
            return None
        return {
            "yhat": round(row["yhat"].values[0], 2),
            "yhat_lower": round(row["yhat_lower"].values[0], 2),
            "yhat_upper": round(row["yhat_upper"].values[0], 2),
        }
