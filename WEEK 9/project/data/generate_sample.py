import pandas as pd
import numpy as np

np.random.seed(42)
dates = pd.date_range(start="2023-01-01", periods=365, freq="D")
trend = np.linspace(100, 200, 365)
seasonality = 30 * np.sin(2 * np.pi * np.arange(365) / 7)
noise = np.random.normal(0, 10, 365)
usage = trend + seasonality + noise

def categorize(u):
    if u < 130:
        return "Low"
    elif u < 170:
        return "Medium"
    else:
        return "High"

df = pd.DataFrame({
    "date": dates.strftime("%Y-%m-%d"),
    "usage": np.round(usage, 2),
    "category": [categorize(u) for u in usage]
})

df.to_csv("sample_usage.csv", index=False)
print("sample_usage.csv generated.")
