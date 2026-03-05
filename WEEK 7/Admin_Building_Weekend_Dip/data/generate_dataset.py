import pandas as pd
import numpy as np

# Generate dates for 30 days
dates = pd.date_range(start='2023-01-01', periods=30)

# Prepare data
data = []
for date in dates:
    day_name = date.day_name()
    for hour in range(24):
        # Weekday vs weekend consumption
        if day_name in ['Saturday', 'Sunday']:
            base = np.random.uniform(15, 20)  # weekend
        else:
            base = np.random.uniform(25, 35)  # weekday
        
        # Office hours slightly higher
        if 8 <= hour <= 18:
            consumption = base + np.random.uniform(0, 5)
        else:
            consumption = base - np.random.uniform(0, 5)
        data.append([date.strftime('%Y-%m-%d'), day_name, hour, round(consumption, 2)])

# Create DataFrame
df = pd.DataFrame(data, columns=['Date', 'Day', 'Hour', 'Energy_Consumption'])

# Save to CSV
df.to_csv('Admin_Building_Sample_Energy_Data.csv', index=False)

print("Sample dataset created: Admin_Building_Sample_Energy_Data.csv")