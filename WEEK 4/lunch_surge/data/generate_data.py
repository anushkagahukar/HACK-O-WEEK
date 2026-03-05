"""
generate_data.py — Synthetic weather + lunch surge data
"""

import numpy as np
import pandas as pd

LOCATIONS = ["Cafeteria A", "Food Court B", "Restaurant C", "Canteen D"]

WEATHER_CONDITIONS = ["Sunny", "Cloudy", "Rainy", "Windy", "Snowy"]


def generate_data(days=180, seed=42):
    np.random.seed(seed)
    records = []

    for day in range(days):
        date = pd.Timestamp("2024-01-01") + pd.Timedelta(days=day)
        month = date.month
        dow = date.dayofweek
        is_weekend = dow >= 5

        # Seasonal temperature (Celsius)
        temp = 15 + 12 * np.sin(2 * np.pi * (month - 3) / 12) + np.random.normal(0, 3)

        # Weather condition probabilities based on temp
        if temp > 25:
            weather_probs = [0.6, 0.2, 0.1, 0.08, 0.02]
        elif temp < 5:
            weather_probs = [0.1, 0.2, 0.2, 0.2, 0.3]
        else:
            weather_probs = [0.3, 0.3, 0.2, 0.15, 0.05]

        weather = np.random.choice(WEATHER_CONDITIONS, p=weather_probs)

        # Weather impact on surge
        weather_factor = {
            "Sunny": 1.3,
            "Cloudy": 1.0,
            "Rainy": 0.75,
            "Windy": 0.85,
            "Snowy": 0.60,
        }[weather]

        humidity = np.clip(80 - temp * 0.8 + np.random.normal(0, 8), 20, 100)
        wind_speed = np.abs(np.random.normal(12, 5))
        feels_like = temp - 0.3 * wind_speed + np.random.normal(0, 1)

        for hour in range(9, 16):     # 9am to 3pm
            for loc in LOCATIONS:
                # Base surge strongest at noon
                hour_factor = np.exp(-0.5 * ((hour - 12.5) / 1.2) ** 2)

                # Temp effect — moderate temps drive more people out
                temp_effect = max(0, 1 - abs(temp - 20) / 25)

                base = {
                    "Cafeteria A": 280,
                    "Food Court B": 350,
                    "Restaurant C": 180,
                    "Canteen D":    220,
                }[loc]

                if is_weekend:
                    base = int(base * 0.4)

                surge = (
                    base
                    * hour_factor
                    * weather_factor
                    * (0.6 + 0.4 * temp_effect)
                    * np.random.uniform(0.88, 1.12)
                )

                records.append({
                    "date":           date,
                    "hour":           hour,
                    "day_of_week":    dow,
                    "is_weekend":     int(is_weekend),
                    "month":          month,
                    "location":       loc,
                    "temperature":    round(temp, 1),
                    "feels_like":     round(feels_like, 1),
                    "humidity":       round(humidity, 1),
                    "wind_speed":     round(wind_speed, 1),
                    "weather":        weather,
                    "weather_factor": weather_factor,
                    "surge_count":    max(0, int(surge)),
                })

    df = pd.DataFrame(records)
    df.to_csv("data/lunch_data.csv", index=False)
    print(f"Generated {len(df):,} records — {days} days × {len(LOCATIONS)} locations × 7 hours")
    return df


if __name__ == "__main__":
    generate_data()
