"""
Utility Functions
=================
Helper functions for data processing and analysis.
"""

import pandas as pd
import numpy as np

def classify_weekday_weekend(day_name):
    """
    Classify a day as weekday or weekend.
    
    Parameters:
    -----------
    day_name : str
        Day of the week (e.g., 'Monday', 'Saturday')
        
    Returns:
    --------
    str
        'Weekend' or 'Weekday'
    """
    weekends = ['Saturday', 'Sunday']
    return 'Weekend' if day_name in weekends else 'Weekday'

def calculate_daily_stats(df):
    """
    Calculate daily total and average energy consumption.
    
    Parameters:
    -----------
    df : DataFrame
        Input dataframe with hourly data
        
    Returns:
    --------
    DataFrame
        Daily statistics with columns: Date, Day, Day_Type, Daily_Total, Daily_Avg, Daily_Min, Daily_Max
    """
    
    # Group by date
    daily_stats = df.groupby('Date').agg({
        'Energy_Consumption': ['sum', 'mean', 'min', 'max'],
        'Day': 'first'  # Get the day of week
    }).reset_index()
    
    # Flatten column names
    daily_stats.columns = ['Date', 'Daily_Total', 'Daily_Avg', 'Daily_Min', 'Daily_Max', 'Day']
    
    # Add day type classification
    daily_stats['Day_Type'] = daily_stats['Day'].apply(classify_weekday_weekend)
    
    # Reorder columns
    daily_stats = daily_stats[['Date', 'Day', 'Day_Type', 'Daily_Total', 'Daily_Avg', 'Daily_Min', 'Daily_Max']]
    
    return daily_stats

def normalize_features(X):
    """
    Normalize features using Min-Max scaling.
    
    Parameters:
    -----------
    X : array-like
        Input features
        
    Returns:
    --------
    array
        Normalized features
    dict
        Scaling parameters (min, max) for inverse transformation
    """
    X = np.asarray(X)
    X_min = X.min(axis=0)
    X_max = X.max(axis=0)
    
    # Prevent division by zero
    X_range = np.where(X_max - X_min == 0, 1, X_max - X_min)
    
    X_normalized = (X - X_min) / X_range
    
    scaling_params = {'min': X_min, 'max': X_max, 'range': X_range}
    
    return X_normalized, scaling_params

def denormalize_features(X_normalized, scaling_params):
    """
    Denormalize features using saved scaling parameters.
    
    Parameters:
    -----------
    X_normalized : array-like
        Normalized features
    scaling_params : dict
        Scaling parameters from normalize_features
        
    Returns:
    --------
    array
        Original scale features
    """
    X_min = scaling_params['min']
    X_range = scaling_params['range']
    
    return X_normalized * X_range + X_min

def calculate_savings_potential(weekday_avg, weekend_avg, target_usage=None):
    """
    Calculate potential energy savings on weekends.
    
    Parameters:
    -----------
    weekday_avg : float
        Average energy consumption on weekdays
    weekend_avg : float
        Average energy consumption on weekends
    target_usage : float, optional
        Target ideal usage level. If None, uses weekend_avg as target.
        
    Returns:
    --------
    dict
        Savings metrics
    """
    
    if target_usage is None:
        target_usage = weekend_avg
    
    weekday_savings = max(0, weekday_avg - target_usage)
    weekend_savings = max(0, weekend_avg - target_usage)
    
    weekday_savings_pct = (weekday_savings / weekday_avg * 100) if weekday_avg > 0 else 0
    weekend_savings_pct = (weekend_savings / weekend_avg * 100) if weekend_avg > 0 else 0
    
    return {
        'weekday_avg': round(weekday_avg, 2),
        'weekend_avg': round(weekend_avg, 2),
        'target_usage': round(target_usage, 2),
        'weekday_savings_potential': round(weekday_savings, 2),
        'weekend_savings_potential': round(weekend_savings, 2),
        'weekday_savings_pct': round(weekday_savings_pct, 2),
        'weekend_savings_pct': round(weekend_savings_pct, 2),
        'dip_percentage': round((weekday_avg - weekend_avg) / weekday_avg * 100, 2)
    }

def print_metrics(metrics):
    """
    Pretty print savings metrics.
    
    Parameters:
    -----------
    metrics : dict
        Metrics dictionary from calculate_savings_potential
    """
    print("\n" + "="*60)
    print("ENERGY SAVINGS ANALYSIS")
    print("="*60)
    print(f"Weekday Average Usage:        {metrics['weekday_avg']:>8.2f} kWh")
    print(f"Weekend Average Usage:        {metrics['weekend_avg']:>8.2f} kWh")
    print(f"Target Usage Level:           {metrics['target_usage']:>8.2f} kWh")
    print("-"*60)
    print(f"Weekend Dip:                  {metrics['dip_percentage']:>8.2f}%")
    print(f"Weekday Savings Potential:    {metrics['weekday_savings_potential']:>8.2f} kWh ({metrics['weekday_savings_pct']:.2f}%)")
    print(f"Weekend Savings Potential:    {metrics['weekend_savings_potential']:>8.2f} kWh ({metrics['weekend_savings_pct']:.2f}%)")
    print("="*60 + "\n")
