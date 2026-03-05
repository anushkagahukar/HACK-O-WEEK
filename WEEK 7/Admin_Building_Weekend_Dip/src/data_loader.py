"""
Data Loading and Preprocessing Module
======================================
Handles loading CSV data and preprocessing energy consumption records.
"""

import pandas as pd
import numpy as np
import os
from .utils import classify_weekday_weekend, calculate_daily_stats

class EnergyDataLoader:
    """
    Loads and preprocesses energy consumption data.
    
    Attributes:
    -----------
    hourly_data : DataFrame
        Raw hourly energy consumption data
    daily_data : DataFrame
        Aggregated daily statistics
    """
    
    def __init__(self):
        """Initialize the data loader."""
        self.hourly_data = None
        self.daily_data = None
        self.is_loaded = False
    
    def load_data(self, filepath):
        """
        Load energy consumption data from CSV file.
        
        Parameters:
        -----------
        filepath : str
            Path to the CSV file
            
        Expected columns:
        - Date: Calendar date (YYYY-MM-DD)
        - Day: Day of the week
        - Hour: Hour of the day (0-23)
        - Energy_Consumption: Energy in kWh
        """
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Data file not found: {filepath}")
        
        try:
            # Load CSV
            self.hourly_data = pd.read_csv(filepath)
            
            # Validate required columns
            required_columns = ['Date', 'Day', 'Hour', 'Energy_Consumption']
            missing_cols = [col for col in required_columns if col not in self.hourly_data.columns]
            
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            # Data type conversion
            self.hourly_data['Date'] = pd.to_datetime(self.hourly_data['Date'])
            self.hourly_data['Hour'] = self.hourly_data['Hour'].astype(int)
            self.hourly_data['Energy_Consumption'] = self.hourly_data['Energy_Consumption'].astype(float)
            
            # Remove duplicates
            self.hourly_data = self.hourly_data.drop_duplicates()
            
            # Handle missing values
            self.hourly_data = self.hourly_data.dropna()
            
            # Calculate daily statistics
            self.daily_data = calculate_daily_stats(self.hourly_data)
            
            self.is_loaded = True
            
            print(f"✓ Data loaded successfully!")
            print(f"  Records: {len(self.hourly_data)} hourly entries")
            print(f"  Days: {len(self.daily_data)} days")
            print(f"  Date range: {self.hourly_data['Date'].min().date()} to {self.hourly_data['Date'].max().date()}")
            
        except Exception as e:
            print(f"✗ Error loading data: {str(e)}")
            raise
    
    def get_hourly_data(self):
        """
        Get hourly energy data.
        
        Returns:
        --------
        DataFrame
            Hourly data with columns: Date, Day, Hour, Energy_Consumption
        """
        if not self.is_loaded:
            raise RuntimeError("Data not loaded. Call load_data() first.")
        return self.hourly_data.copy()
    
    def get_daily_data(self):
        """
        Get daily aggregated data.
        
        Returns:
        --------
        DataFrame
            Daily statistics with columns: Date, Day, Day_Type, Daily_Total, Daily_Avg
        """
        if not self.is_loaded:
            raise RuntimeError("Data not loaded. Call load_data() first.")
        return self.daily_data.copy()
    
    def get_weekday_weeknd_data(self):
        """
        Separate data into weekday and weekend.
        
        Returns:
        --------
        tuple
            (weekday_data, weekend_data) DataFrames
        """
        if not self.is_loaded:
            raise RuntimeError("Data not loaded. Call load_data() first.")
        
        weekday_data = self.daily_data[self.daily_data['Day_Type'] == 'Weekday'].copy()
        weekend_data = self.daily_data[self.daily_data['Day_Type'] == 'Weekend'].copy()
        
        return weekday_data, weekend_data
    
    def get_summary_stats(self):
        """
        Get summary statistics of the dataset.
        
        Returns:
        --------
        dict
            Summary statistics
        """
        if not self.is_loaded:
            raise RuntimeError("Data not loaded. Call load_data() first.")
        
        hourly_stats = self.hourly_data['Energy_Consumption'].describe()
        
        weekday_data, weekend_data = self.get_weekday_weeknd_data()
        
        stats = {
            'total_days': len(self.daily_data),
            'total_weekdays': len(weekday_data),
            'total_weekends': len(weekend_data),
            'hourly_min': round(hourly_stats['min'], 2),
            'hourly_max': round(hourly_stats['max'], 2),
            'hourly_mean': round(hourly_stats['mean'], 2),
            'hourly_std': round(hourly_stats['std'], 2),
            'daily_mean_weekday': round(weekday_data['Daily_Avg'].mean(), 2),
            'daily_mean_weekend': round(weekend_data['Daily_Avg'].mean(), 2),
        }
        
        return stats
    
    def print_summary(self):
        """Print summary statistics to console."""
        if not self.is_loaded:
            raise RuntimeError("Data not loaded. Call load_data() first.")
        
        stats = self.get_summary_stats()
        
        print("\n" + "="*60)
        print("DATA SUMMARY STATISTICS")
        print("="*60)
        print(f"Total Days:                   {stats['total_days']}")
        print(f"  - Weekdays:                 {stats['total_weekdays']}")
        print(f"  - Weekends:                 {stats['total_weekends']}")
        print("-"*60)
        print("Hourly Energy Consumption (kWh):")
        print(f"  - Min:                      {stats['hourly_min']}")
        print(f"  - Max:                      {stats['hourly_max']}")
        print(f"  - Mean:                     {stats['hourly_mean']}")
        print(f"  - StdDev:                   {stats['hourly_std']}")
        print("-"*60)
        print("Daily Average (kWh):")
        print(f"  - Weekday Average:          {stats['daily_mean_weekday']}")
        print(f"  - Weekend Average:          {stats['daily_mean_weekend']}")
        print("="*60 + "\n")

# Convenience function for quick loading
def load_energy_data(filepath):
    """
    Quick function to load energy data.
    
    Parameters:
    -----------
    filepath : str
        Path to CSV file
        
    Returns:
    --------
    tuple
        (hourly_data, daily_data) DataFrames
    """
    loader = EnergyDataLoader()
    loader.load_data(filepath)
    return loader.get_hourly_data(), loader.get_daily_data()
