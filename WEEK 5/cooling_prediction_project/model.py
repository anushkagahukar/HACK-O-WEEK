"""
model.py
--------
Generates synthetic data and trains a Decision Tree Classifier
for cooling demand prediction.
"""

import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# ── 1. SYNTHETIC DATA GENERATOR ──────────────────────────────────────────────

def generate_data(n: int = 100) -> pd.DataFrame:
    """Create a small synthetic dataset with 100 rows across 4 zones."""
    np.random.seed(42)
    zones = ["Zone A", "Zone B", "Zone C", "Zone D"]

    data = {
        "zone":        np.random.choice(zones, n),
        "temperature": np.random.randint(18, 38, n),   # °C
        "occupancy":   np.random.randint(1, 30, n),    # people
        "humidity":    np.random.randint(30, 85, n),   # %
    }
    df = pd.DataFrame(data)

    # Rule-based label: cooling needed when it's hot, crowded, or humid
    df["cooling_needed"] = (
        (df["temperature"] >= 27) |
        (df["occupancy"]   >= 15) |
        (df["humidity"]    >= 65)
    ).astype(int)

    return df


# ── 2. MODEL TRAINING ─────────────────────────────────────────────────────────

def train_model(df: pd.DataFrame):
    """
    Train a Decision Tree Classifier.
    Returns the trained model and test accuracy.
    """
    features = ["temperature", "occupancy", "humidity"]
    X = df[features]
    y = df["cooling_needed"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = DecisionTreeClassifier(max_depth=4, random_state=42)
    model.fit(X_train, y_train)

    accuracy = accuracy_score(y_test, model.predict(X_test))
    return model, round(accuracy * 100, 1)


# ── 3. SINGLE PREDICTION ──────────────────────────────────────────────────────

def predict(model, temperature: float, occupancy: int, humidity: float) -> int:
    """Return 1 (cooling needed) or 0 (not needed) for given inputs."""
    X = pd.DataFrame([[temperature, occupancy, humidity]],
                     columns=["temperature", "occupancy", "humidity"])
    return int(model.predict(X)[0])
