"""
generate_data.py — Synthetic sensor vehicle count data
"""

import numpy as np
import pandas as pd

INTERSECTIONS = ["North Gate", "South Gate", "East Junction", "West Junction", "City Center"]

def generate_sensor_data(days=30, seed=42):
    np.random.seed(seed)
    records = []

    for day in range(days):
        for hour in range(24):
            for minute in range(0, 60, 5):   # every 5 minutes
                time = pd.Timestamp("2024-01-01") + pd.Timedelta(days=day, hours=hour, minutes=minute)
                dow  = time.dayofweek
                is_weekend = dow >= 5

                # Rush hour pattern
                if hour in [7, 8, 9]:        base = 180
                elif hour in [17, 18, 19]:   base = 200
                elif hour in [12, 13]:       base = 120
                elif 0 <= hour <= 5:         base = 10
                else:                        base = 70

                if is_weekend:
                    base = int(base * 0.55)

                for sensor in INTERSECTIONS:
                    count = max(0, int(base + np.random.normal(0, base * 0.15)))
                    # Inject anomalies randomly (~2%)
                    anomaly = np.random.random() < 0.02
                    if anomaly:
                        count = count * np.random.choice([3, 4, 0])  # spike or dropout

                    records.append({
                        "timestamp":    time,
                        "hour":         hour,
                        "minute":       minute,
                        "day_of_week":  dow,
                        "is_weekend":   int(is_weekend),
                        "intersection": sensor,
                        "vehicle_count":count,
                        "is_anomaly":   int(anomaly),
                    })

    df = pd.DataFrame(records)
    df.to_csv("data/sensor_data.csv", index=False)
    print(f"Generated {len(df):,} records across {len(INTERSECTIONS)} intersections.")
    return df


if __name__ == "__main__":
    generate_sensor_data()
