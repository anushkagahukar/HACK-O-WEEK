"""
Admin Building Weekend Dip - Example Analysis Script
=====================================================
This script demonstrates how to use the modules programmatically
for custom analysis without the dashboard.

Run this script with:
    python analysis_example.py
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from src.data_loader import EnergyDataLoader
from src.clustering import EnergyClusterer
from src.regression import EnergyRegressor
from src.utils import calculate_savings_potential, print_metrics

def main():
    """Run complete analysis pipeline."""
    
    print("\n" + "="*70)
    print("ADMIN BUILDING WEEKEND DIP - COMPREHENSIVE ANALYSIS")
    print("="*70 + "\n")
    
    # ========================================================================
    # STEP 1: LOAD AND PREPROCESS DATA
    # ========================================================================
    
    print("STEP 1: Loading and Preprocessing Data")
    print("-" * 70)
    
    # Check if sample data exists, if not generate it
    data_path = 'data/energy_data.csv'
    if not os.path.exists(data_path):
        print("Sample data not found. Generating...")
        from generate_sample_data import generate_sample_data
        generate_sample_data(num_days=365, output_path=data_path)
    
    # Load data
    loader = EnergyDataLoader()
    loader.load_data(data_path)
    
    # Get data
    hourly_data = loader.get_hourly_data()
    daily_data = loader.get_daily_data()
    
    # Print summary
    loader.print_summary()
    
    # ========================================================================
    # STEP 2: PERFORM CLUSTERING
    # ========================================================================
    
    print("\nSTEP 2: K-Means Clustering Analysis")
    print("-" * 70)
    
    clusterer = EnergyClusterer()
    clusterer.fit(daily_data, n_clusters=3, random_state=42)
    
    # Get labeled data
    labeled_data = clusterer.get_labeled_data()
    
    # Print cluster summary
    clusterer.print_cluster_summary()
    
    # Save clustering visualization
    fig = clusterer.visualize_clusters(figsize=(12, 7))
    plt.savefig('output_cluster_visualization.png', dpi=300, bbox_inches='tight')
    print("✓ Cluster visualization saved as 'output_cluster_visualization.png'")
    plt.close()
    
    # ========================================================================
    # STEP 3: PERFORM REGRESSION AND FORECASTING
    # ========================================================================
    
    print("\nSTEP 3: Regression & Energy Forecasting")
    print("-" * 70)
    
    regressor = EnergyRegressor()
    regressor.fit(labeled_data, degree=2)
    regressor.forecast(days_into_future=30)
    
    # Print forecast summary
    regressor.print_forecast_summary()
    
    # Save forecast visualization
    fig = regressor.visualize_forecasts(labeled_data, figsize=(14, 10))
    plt.savefig('output_forecast_visualization.png', dpi=300, bbox_inches='tight')
    print("✓ Forecast visualization saved as 'output_forecast_visualization.png'")
    plt.close()
    
    # ========================================================================
    # STEP 4: CALCULATE SAVINGS POTENTIAL
    # ========================================================================
    
    print("\nSTEP 4: Savings Potential Analysis")
    print("-" * 70)
    
    # Separate weekday and weekend data
    weekday_data = daily_data[daily_data['Day_Type'] == 'Weekday']
    weekend_data = daily_data[daily_data['Day_Type'] == 'Weekend']
    
    # Calculate statistics
    weekday_avg = weekday_data['Daily_Avg'].mean()
    weekend_avg = weekend_data['Daily_Avg'].mean()
    
    # Calculate savings potential
    savings_metrics = calculate_savings_potential(weekday_avg, weekend_avg)
    print_metrics(savings_metrics)
    
    # ========================================================================
    # STEP 5: DETAILED ANALYSIS BY CLUSTER
    # ========================================================================
    
    print("\nSTEP 5: Detailed Analysis by Cluster")
    print("-" * 70)
    
    cluster_info = clusterer.get_cluster_info()
    
    for _, cluster_row in cluster_info.iterrows():
        usage_level = cluster_row['Usage_Level']
        print(f"\n{usage_level.upper()} USAGE CLUSTER:")
        print(f"  Days in cluster:            {int(cluster_row['Count'])}")
        print(f"  Average daily consumption:  {cluster_row['Avg_Daily_Consumption']:.2f} kWh")
        print(f"  Total daily consumption:    {cluster_row['Total_Daily_Consumption']:.2f} kWh")
        print(f"  Min daily consumption:      {cluster_row['Min_Daily_Consumption']:.2f} kWh")
        print(f"  Max daily consumption:      {cluster_row['Max_Daily_Consumption']:.2f} kWh")
        print(f"  Weekdays:                   {int(cluster_row['Weekday_Count'])}")
        print(f"  Weekends:                   {int(cluster_row['Weekend_Count'])}")
    
    # ========================================================================
    # STEP 6: GENERATE REPORTS
    # ========================================================================
    
    print("\n\nSTEP 6: Generating Reports")
    print("-" * 70)
    
    # Generate daily summary report
    summary_report = daily_data[[
        'Date', 'Day', 'Day_Type', 'Daily_Avg', 'Daily_Total'
    ]].copy()
    
    # Add cluster information
    summary_report['Cluster'] = labeled_data['Cluster']
    summary_report['Usage_Level'] = labeled_data['Usage_Level']
    
    # Save to CSV
    summary_report.to_csv('output_daily_summary.csv', index=False)
    print("✓ Daily summary report saved as 'output_daily_summary.csv'")
    
    # ========================================================================
    # STEP 7: CREATE VISUALIZATION DASHBOARD (Multi-chart)
    # ========================================================================
    
    print("\nSTEP 7: Creating Comprehensive Dashboard")
    print("-" * 70)
    
    fig = plt.figure(figsize=(16, 12))
    
    # 1. Cluster pie chart
    ax1 = plt.subplot(2, 3, 1)
    cluster_dist = cluster_info.set_index('Usage_Level')['Count']
    colors = ['#2ecc71', '#f39c12', '#e74c3c']
    ax1.pie(cluster_dist.values, labels=cluster_dist.index, autopct='%1.1f%%',
           colors=colors[:len(cluster_dist)], startangle=90)
    ax1.set_title('Cluster Distribution', fontweight='bold')
    
    # 2. Weekday vs Weekend comparison
    ax2 = plt.subplot(2, 3, 2)
    day_types = ['Weekday', 'Weekend']
    avg_values = [
        weekday_data['Daily_Avg'].mean(),
        weekend_data['Daily_Avg'].mean()
    ]
    bars = ax2.bar(day_types, avg_values, color=['#3498db', '#2ecc71'], alpha=0.8)
    ax2.set_ylabel('Average Daily Consumption (kWh)', fontweight='bold')
    ax2.set_title('Weekday vs Weekend Usage', fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}', ha='center', va='bottom', fontweight='bold')
    
    # 3. Hourly pattern
    ax3 = plt.subplot(2, 3, 3)
    hourly_avg = hourly_data.groupby('Hour')['Energy_Consumption'].mean()
    ax3.plot(hourly_avg.index, hourly_avg.values, marker='o', linewidth=2, color='#3498db')
    ax3.fill_between(hourly_avg.index, hourly_avg.values, alpha=0.3, color='#3498db')
    ax3.set_xlabel('Hour of Day', fontweight='bold')
    ax3.set_ylabel('Average Energy (kWh)', fontweight='bold')
    ax3.set_title('Daily Hourly Pattern', fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # 4. Daily consumption over time
    ax4 = plt.subplot(2, 3, 4)
    ax4.plot(daily_data['Daily_Avg'], linewidth=1.5, alpha=0.7, color='#3498db', label='Daily Average')
    ax4.axhline(y=weekday_avg, color='#e74c3c', linestyle='--', linewidth=2, label='Weekday Avg')
    ax4.axhline(y=weekend_avg, color='#2ecc71', linestyle='--', linewidth=2, label='Weekend Avg')
    ax4.set_ylabel('Consumption (kWh)', fontweight='bold')
    ax4.set_xlabel('Days', fontweight='bold')
    ax4.set_title('Energy Consumption Timeline', fontweight='bold')
    ax4.legend(loc='best')
    ax4.grid(True, alpha=0.3)
    
    # 5. Distribution by day of week
    ax5 = plt.subplot(2, 3, 5)
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_by_day = daily_data.groupby('Day')['Daily_Avg'].mean().reindex(day_order)
    colors_days = ['#3498db']*5 + ['#2ecc71']*2
    ax5.bar(range(len(daily_by_day)), daily_by_day.values, color=colors_days, alpha=0.8)
    ax5.set_xticks(range(len(daily_by_day)))
    ax5.set_xticklabels([d[:3] for d in daily_by_day.index], rotation=45)
    ax5.set_ylabel('Average Consumption (kWh)', fontweight='bold')
    ax5.set_title('Consumption by Day of Week', fontweight='bold')
    ax5.grid(axis='y', alpha=0.3)
    
    # 6. Cluster characteristics
    ax6 = plt.subplot(2, 3, 6)
    cluster_names = cluster_info['Usage_Level'].values
    cluster_means = cluster_info['Avg_Daily_Consumption'].values
    bars = ax6.barh(cluster_names, cluster_means, color=['#2ecc71', '#f39c12', '#e74c3c'], alpha=0.8)
    ax6.set_xlabel('Average Daily Consumption (kWh)', fontweight='bold')
    ax6.set_title('Cluster Characteristics', fontweight='bold')
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax6.text(width, bar.get_y() + bar.get_height()/2.,
                f'{cluster_means[i]:.1f}', ha='left', va='center', fontweight='bold')
    
    plt.suptitle('Admin Building Weekend Dip - Comprehensive Analysis Dashboard', 
                fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig('output_comprehensive_dashboard.png', dpi=300, bbox_inches='tight')
    print("✓ Comprehensive dashboard saved as 'output_comprehensive_dashboard.png'")
    plt.close()
    
    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print("\nGenerated Files:")
    print("  ✓ output_cluster_visualization.png")
    print("  ✓ output_forecast_visualization.png")
    print("  ✓ output_comprehensive_dashboard.png")
    print("  ✓ output_daily_summary.csv")
    print("\nKey Findings:")
    print(f"  • Weekend energy dip: {savings_metrics['dip_percentage']:.2f}%")
    print(f"  • Potential weekday savings: {savings_metrics['weekday_savings_potential']:.2f} kWh")
    print(f"  • Dataset covers {len(daily_data)} days")
    print(f"  • Three usage clusters identified: High, Medium, Low")
    print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    main()
