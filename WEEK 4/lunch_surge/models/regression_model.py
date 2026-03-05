"""
regression_model.py — Linear Regression: weather → lunch surge prediction
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error


NUMERIC_FEATURES  = ["temperature", "feels_like", "humidity", "wind_speed", "hour", "is_weekend", "month"]
CATEGORIC_FEATURES = ["weather", "location"]
ALL_FEATURES       = NUMERIC_FEATURES + CATEGORIC_FEATURES
TARGET             = "surge_count"


def build_pipeline():
    numeric_transformer  = StandardScaler()
    categoric_transformer = OneHotEncoder(handle_unknown="ignore", sparse_output=False)

    preprocessor = ColumnTransformer([
        ("num", numeric_transformer,  NUMERIC_FEATURES),
        ("cat", categoric_transformer, CATEGORIC_FEATURES),
    ])

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("regressor",    LinearRegression()),
    ])
    return pipeline


def train_model(df: pd.DataFrame):
    X = df[ALL_FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    y_pred = np.clip(y_pred, 0, None)

    metrics = {
        "MAE":  round(mean_absolute_error(y_test, y_pred), 2),
        "RMSE": round(np.sqrt(mean_squared_error(y_test, y_pred)), 2),
        "R2":   round(r2_score(y_test, y_pred), 4),
        "samples": len(df),
    }
    return pipeline, metrics


def predict_surge(pipeline, temperature, feels_like, humidity,
                  wind_speed, hour, is_weekend, month, weather, location):
    row = pd.DataFrame([{
        "temperature": temperature,
        "feels_like":  feels_like,
        "humidity":    humidity,
        "wind_speed":  wind_speed,
        "hour":        hour,
        "is_weekend":  int(is_weekend),
        "month":       month,
        "weather":     weather,
        "location":    location,
    }])
    pred = pipeline.predict(row)[0]
    return max(0, int(pred))


def get_feature_importance(pipeline):
    """Return top features by absolute coefficient."""
    reg   = pipeline.named_steps["regressor"]
    prep  = pipeline.named_steps["preprocessor"]
    coefs = reg.coef_

    num_names = NUMERIC_FEATURES
    cat_names = list(prep.named_transformers_["cat"].get_feature_names_out(CATEGORIC_FEATURES))
    all_names = num_names + cat_names

    importance = pd.DataFrame({
        "Feature":    all_names,
        "Coefficient": coefs,
        "AbsCoef":    np.abs(coefs),
    }).sort_values("AbsCoef", ascending=False).head(15)
    return importance
