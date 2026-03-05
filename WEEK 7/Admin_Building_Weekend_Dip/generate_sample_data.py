"""
Generate Sample Energy Consumption Dataset
===========================================
This script generates a realistic sample dataset of energy consumption 
for a building over several months. The data includes:
- Date: Calendar date
- Day: Day of the week
- Hour: Hour of the day (0-23)
- Energy_Consumption: Energy consumed in kWh

The data simulates realistic patterns:
- Higher consumption during weekdays (business hours)
- Lower consumption on weekends
- Daily patterns with peaks during business hours
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_sample_data(num_days=365, output_path='data/energy_data.csv'):
    """
    Generate sample energy consumption dataset.
    
    Parameters:
    -----------
    num_days : int
        Number of days of data to generate (default: 365)
    output_path : str
        Path to save the CSV file
    """
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Generate date range
    start_date = datetime(2023, 1, 1)
    dates = pd.date_range(start=start_date, periods=num_days * 24, freq='H')
    
    # Create dataframe
    data = []
    
    for date in dates:
        day_name = date.strftime('%A')  # e.g., 'Monday'
        hour = date.hour
        
        # Determine if it's a weekend
        is_weekend = day_name in ['Saturday', 'Sunday']
        
        # Base consumption patterns
        if is_weekend:
            # Weekends: lower base consumption
            if 0 <= hour < 6:
                base_consumption = 15 + np.random.normal(0, 2)  # Night - minimal
            elif 6 <= hour < 9:
                base_consumption = 20 + np.random.normal(0, 2)  # Early morning
            elif 9 <= hour < 17:
                base_consumption = 35 + np.random.normal(0, 3)  # Day hours
            elif 17 <= hour < 21:
                base_consumption = 40 + np.random.normal(0, 2)  # Evening
            else:
                base_consumption = 20 + np.random.normal(0, 2)  # Night
        else:
            # Weekdays: higher business consumption
            if 0 <= hour < 6:
                base_consumption = 25 + np.random.normal(0, 2)  # Night - HVAC
            elif 6 <= hour < 9:
                base_consumption = 45 + np.random.normal(0, 3)  # Morning startup
            elif 9 <= hour < 12:
                base_consumption = 75 + np.random.normal(0, 5)  # Peak morning
            elif 12 <= hour < 14:
                base_consumption = 70 + np.random.normal(0, 5)  # Lunch period
            elif 14 <= hour < 17:
                base_consumption = 80 + np.random.normal(0, 5)  # Afternoon peak
            elif 17 <= hour < 21:
                base_consumption = 50 + np.random.normal(0, 3)  # Evening wind-down
            else:
                base_consumption = 30 + np.random.normal(0, 2)  # Night
        
        # Ensure non-negative consumption
        energy_consumption = max(10, base_consumption)
        
        data.append({
            'Date': date.strftime('%Y-%m-%d'),
            'Day': day_name,
            'Hour': hour,
            'Energy_Consumption': round(energy_consumption, 2)
        })
    
    df = pd.DataFrame(data)
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    print(f"✓ Sample dataset generated successfully!")
    print(f"  Location: {output_path}")
    print(f"  Shape: {df.shape}")
    print(f"  Date range: {df['Date'].min()} to {df['Date'].max()}")
    print(f"\nFirst few rows:")
    print(df.head(10))
    
    return df

if __name__ == '__main__':
    # Generate sample data
    generate_sample_data(num_days=365, output_path='data/energy_data.csv')
