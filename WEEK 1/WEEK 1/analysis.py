import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 6)

# ============================================================================
# 1. LOAD DATA
# ============================================================================
print("=" * 80)
print("ELECTRICITY APARTMENT CONSUMPTION ANALYSIS")
print("=" * 80)

# Load CSV data
csv_path = r'electricity_apartment-summary.csv'
df = pd.read_csv(csv_path, index_col=0)
df.index = pd.to_datetime(df.index, utc=True)

# Load JSON data
json_path = r'electricity_apartment-group_details.json'
with open(json_path, 'r') as f:
    group_details = json.load(f)

print(f"\n✓ Data loaded successfully")
print(f"  - CSV shape: {df.shape}")
print(f"  - Date range: {df.index.min()} to {df.index.max()}")

# ============================================================================
# 2. DATA OVERVIEW
# ============================================================================
print("\n" + "=" * 80)
print("DATA OVERVIEW")
print("=" * 80)

print(f"\nDataset Info:")
print(f"  - Total records: {len(df)}")
print(f"  - Time period: {(df.index.max() - df.index.min()).days} days")
print(f"  - Number of apartments sampled: {int(df['Count'].iloc[0])}")

print(f"\nColumns: {list(df.columns)}")
print(f"\nFirst few rows:")
print(df.head())

# ============================================================================
# 3. GROUP DETAILS ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("GROUP DEMOGRAPHICS")
print("=" * 80)

print("\nSocio-Economic Categories:")
for cat, count in sorted(group_details['socioCat'].items(), key=lambda x: x[1], reverse=True):
    print(f"  - {cat}: {count}")

print("\nDwelling Type:")
for dtype, count in group_details['dwelling type'].items():
    print(f"  - {dtype}: {count}")

print("\nDwelling Ownership:")
for ownership, count in sorted(group_details['dwelling ownership'].items(), key=lambda x: x[1], reverse=True):
    print(f"  - {ownership}: {count}")

print("\nPlace Location:")
for location, count in sorted(group_details['placeLocation'].items(), key=lambda x: x[1], reverse=True):
    print(f"  - {location}: {count}")

# ============================================================================
# 4. STATISTICAL SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("ELECTRICITY CONSUMPTION STATISTICS")
print("=" * 80)

print("\nOverall Statistics (Wh):")
print(f"  - Mean consumption: {df['Mean'].mean():.2f} Wh")
print(f"  - Median consumption: {df['Median'].median():.2f} Wh")
print(f"  - Min consumption: {df['Min'].min():.2f} Wh")
print(f"  - Max consumption: {df['Max'].max():.2f} Wh")
print(f"  - Std Dev: {df['Mean'].std():.2f} Wh")

print("\nConsumption Range:")
print(f"  - Minimum recorded: {df['Min'].min():.2f} Wh")
print(f"  - Maximum recorded: {df['Max'].max():.2f} Wh")
print(f"  - Variability (Max/Min ratio): {df['Max'].max() / (df['Min'].min() + 1):.2f}x")

# ============================================================================
# 5. TIME-BASED ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("TIME-BASED PATTERNS")
print("=" * 80)

# Extract time components
df['hour'] = df.index.hour
df['date'] = df.index.date
df['day_of_week'] = df.index.day_name()

# Hourly patterns
hourly_stats = df.groupby('hour')['Mean'].agg(['mean', 'min', 'max', 'std'])
peak_hour = hourly_stats['mean'].idxmax()
low_hour = hourly_stats['mean'].idxmin()

print(f"\nHourly Consumption Patterns:")
print(f"  - Peak hour: {peak_hour:02d}:00 ({hourly_stats.loc[peak_hour, 'mean']:.2f} Wh)")
print(f"  - Low hour: {low_hour:02d}:00 ({hourly_stats.loc[low_hour, 'mean']:.2f} Wh)")
print(f"  - Peak/Low ratio: {hourly_stats.loc[peak_hour, 'mean'] / hourly_stats.loc[low_hour, 'mean']:.2f}x")

# Daily patterns
daily_stats = df.groupby('date')['Mean'].agg(['sum', 'mean', 'max'])
print(f"\nDaily Consumption Patterns:")
print(f"  - Avg daily consumption: {daily_stats['sum'].mean():.2f} Wh")
print(f"  - Max daily consumption: {daily_stats['sum'].max():.2f} Wh")
print(f"  - Min daily consumption: {daily_stats['sum'].min():.2f} Wh")

# Weekly patterns
weekly_stats = df.groupby('day_of_week')['Mean'].agg(['mean', 'std'])
print(f"\nWeekly Patterns:")
days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
for day in days_order:
    if day in weekly_stats.index:
        print(f"  - {day}: {weekly_stats.loc[day, 'mean']:.2f} ± {weekly_stats.loc[day, 'std']:.2f} Wh")

# ============================================================================
# 6. CONSUMPTION VARIABILITY
# ============================================================================
print("\n" + "=" * 80)
print("CONSUMPTION VARIABILITY & OUTLIERS")
print("=" * 80)

# Calculate quartile statistics
q1 = df['Mean'].quantile(0.25)
q3 = df['Mean'].quantile(0.75)
iqr = q3 - q1
lower_bound = q1 - 1.5 * iqr
upper_bound = q3 + 1.5 * iqr

outliers = df[(df['Mean'] < lower_bound) | (df['Mean'] > upper_bound)]

print(f"\nQuartile Analysis:")
print(f"  - Q1 (25%): {q1:.2f} Wh")
print(f"  - Q2 (50%): {df['Mean'].median():.2f} Wh")
print(f"  - Q3 (75%): {q3:.2f} Wh")
print(f"  - IQR: {iqr:.2f} Wh")

print(f"\nOutliers detected: {len(outliers)} ({len(outliers)/len(df)*100:.2f}%)")
if len(outliers) > 0:
    print(f"  - Outlier range: < {lower_bound:.2f} or > {upper_bound:.2f}")

# ============================================================================
# 7. VISUALIZATIONS
# ============================================================================
print("\n" + "=" * 80)
print("GENERATING VISUALIZATIONS")
print("=" * 80)

# Reset for plotting
df_plot = df.copy()

# Figure 1: Time Series
fig, axes = plt.subplots(2, 1, figsize=(14, 10))

# Mean consumption over time
axes[0].plot(df_plot.index, df_plot['Mean'], label='Mean', color='steelblue', linewidth=1.5)
axes[0].fill_between(df_plot.index, df_plot['Min'], df_plot['Max'], alpha=0.2, color='steelblue', label='Min-Max Range')
axes[0].set_title('Electricity Consumption Over Time (Mean ± Min-Max Range)', fontsize=12, fontweight='bold')
axes[0].set_ylabel('Consumption (Wh)')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Median consumption
axes[1].plot(df_plot.index, df_plot['Median'], label='Median', color='coral', linewidth=1.5)
axes[1].set_title('Median Electricity Consumption Over Time', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Date')
axes[1].set_ylabel('Consumption (Wh)')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('01_timeseries_analysis.png', dpi=300, bbox_inches='tight')
print("\n✓ Saved: 01_timeseries_analysis.png")
plt.close()

# Figure 2: Hourly and Daily Patterns
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Hourly pattern
hourly_data = df_plot.groupby('hour')['Mean'].mean()
axes[0].bar(hourly_data.index, hourly_data.values, color='steelblue', alpha=0.7)
axes[0].set_title('Average Consumption by Hour of Day', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Hour')
axes[0].set_ylabel('Consumption (Wh)')
axes[0].grid(True, alpha=0.3, axis='y')

# Weekly pattern
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
weekly_data = df_plot.groupby('day_of_week')['Mean'].mean().reindex(day_order)
colors = ['#FF6B6B' if day in ['Saturday', 'Sunday'] else 'steelblue' for day in day_order]
axes[1].bar(range(len(day_order)), weekly_data.values, color=colors, alpha=0.7)
axes[1].set_xticks(range(len(day_order)))
axes[1].set_xticklabels([d[:3] for d in day_order], rotation=45)
axes[1].set_title('Average Consumption by Day of Week', fontsize=12, fontweight='bold')
axes[1].set_ylabel('Consumption (Wh)')
axes[1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('02_hourly_daily_patterns.png', dpi=300, bbox_inches='tight')
print("✓ Saved: 02_hourly_daily_patterns.png")
plt.close()

# Figure 3: Distribution Analysis
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Histogram of Mean consumption
axes[0, 0].hist(df_plot['Mean'], bins=50, color='steelblue', alpha=0.7, edgecolor='black')
axes[0, 0].axvline(df_plot['Mean'].mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {df_plot["Mean"].mean():.2f}')
axes[0, 0].axvline(df_plot['Mean'].median(), color='orange', linestyle='--', linewidth=2, label=f'Median: {df_plot["Mean"].median():.2f}')
axes[0, 0].set_title('Distribution of Mean Consumption', fontsize=12, fontweight='bold')
axes[0, 0].set_xlabel('Consumption (Wh)')
axes[0, 0].set_ylabel('Frequency')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# Box plot
axes[0, 1].boxplot([df_plot['Mean'], df_plot['Median'], df_plot['Max']], labels=['Mean', 'Median', 'Max'])
axes[0, 1].set_title('Box Plot of Consumption Metrics', fontsize=12, fontweight='bold')
axes[0, 1].set_ylabel('Consumption (Wh)')
axes[0, 1].grid(True, alpha=0.3, axis='y')

# Daily sum distribution
daily_sum = df_plot.groupby('date')['Mean'].sum()
axes[1, 0].hist(daily_sum, bins=30, color='coral', alpha=0.7, edgecolor='black')
axes[1, 0].axvline(daily_sum.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {daily_sum.mean():.2f}')
axes[1, 0].set_title('Distribution of Daily Total Consumption', fontsize=12, fontweight='bold')
axes[1, 0].set_xlabel('Daily Consumption (Wh)')
axes[1, 0].set_ylabel('Frequency')
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

# QQ plot for normality
from scipy import stats
stats.probplot(df_plot['Mean'], dist="norm", plot=axes[1, 1])
axes[1, 1].set_title('Q-Q Plot (Normality Check)', fontsize=12, fontweight='bold')
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('03_distribution_analysis.png', dpi=300, bbox_inches='tight')
print("✓ Saved: 03_distribution_analysis.png")
plt.close()

# Figure 4: Consumption Range Analysis
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Min, Mean, Max comparison
daily_stats_plot = df_plot.groupby('date')[['Min', 'Mean', 'Max']].mean()
axes[0].plot(daily_stats_plot.index, daily_stats_plot['Min'], label='Min', marker='o', markersize=3, color='green', alpha=0.7)
axes[0].plot(daily_stats_plot.index, daily_stats_plot['Mean'], label='Mean', marker='s', markersize=3, color='blue', alpha=0.7)
axes[0].plot(daily_stats_plot.index, daily_stats_plot['Max'], label='Max', marker='^', markersize=3, color='red', alpha=0.7)
axes[0].fill_between(daily_stats_plot.index, daily_stats_plot['Min'], daily_stats_plot['Max'], alpha=0.1, color='gray')
axes[0].set_title('Daily Min, Mean, Max Consumption Trend', fontsize=12, fontweight='bold')
axes[0].set_ylabel('Consumption (Wh)')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Variability (spread) over time
df_plot['Range'] = df_plot['Max'] - df_plot['Min']
daily_range = df_plot.groupby('date')['Range'].mean()
axes[1].plot(daily_range.index, daily_range.values, color='purple', linewidth=2)
axes[1].fill_between(daily_range.index, daily_range.values, alpha=0.3, color='purple')
axes[1].set_title('Daily Consumption Variability (Max - Min)', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Date')
axes[1].set_ylabel('Range (Wh)')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('04_consumption_range_analysis.png', dpi=300, bbox_inches='tight')
print("✓ Saved: 04_consumption_range_analysis.png")
plt.close()

# ============================================================================
# 8. ADVANCED METRICS
# ============================================================================
print("\n" + "=" * 80)
print("ADVANCED METRICS")
print("=" * 80)

# Load demand coefficient calculation
total_daily_consumption = df_plot.groupby('date')['Mean'].sum().sum()
print(f"\nEnergy Consumption Summary:")
print(f"  - Total consumption (analysis period): {total_daily_consumption:.2f} Wh")
print(f"  - Average daily consumption: {daily_sum.mean():.2f} Wh")
print(f"  - Per apartment average (daily): {daily_sum.mean() / 67:.2f} Wh")

# Variance analysis
print(f"\nVariance Analysis:")
print(f"  - Coefficient of Variation: {df_plot['Mean'].std() / df_plot['Mean'].mean():.4f}")
print(f"  - Skewness: {df_plot['Mean'].skew():.4f}")
print(f"  - Kurtosis: {df_plot['Mean'].kurtosis():.4f}")

# Peak vs Off-peak
peak_hours = [8, 9, 10, 11, 12, 18, 19, 20, 21]  # Typical peak hours
peak_consumption = df_plot[df_plot['hour'].isin(peak_hours)]['Mean'].mean()
off_peak_consumption = df_plot[~df_plot['hour'].isin(peak_hours)]['Mean'].mean()

print(f"\nPeak vs Off-peak Analysis:")
print(f"  - Peak hours (8-12, 18-21): {peak_consumption:.2f} Wh")
print(f"  - Off-peak hours: {off_peak_consumption:.2f} Wh")
print(f"  - Peak/Off-peak ratio: {peak_consumption / off_peak_consumption:.2f}x")

# ============================================================================
# 9. SUMMARY REPORT
# ============================================================================
print("\n" + "=" * 80)
print("KEY INSIGHTS & SUMMARY")
print("=" * 80)

print(f"""
📊 DATASET CHARACTERISTICS:
   • {len(df)} records spanning {(df.index.max() - df.index.min()).days} days
   • {int(df['Count'].iloc[0])} apartment units monitored
   • {67}/{67} apartments are in city-centre/urban location (53 out of 67)
   • {47}/{67} are renters, {16}/{67} are home-owners, {4}/{67} are group-renters

⚡ CONSUMPTION PATTERNS:
   • Peak consumption at {peak_hour:02d}:00 ({hourly_stats.loc[peak_hour, 'mean']:.2f} Wh)
   • Lowest consumption at {low_hour:02d}:00 ({hourly_stats.loc[low_hour, 'mean']:.2f} Wh)
   • Daily average: {daily_sum.mean():.2f} Wh per day
   • Peak-to-minimum variation: {hourly_stats.loc[peak_hour, 'mean'] / hourly_stats.loc[low_hour, 'mean']:.2f}x

📈 STATISTICAL SUMMARY:
   • Mean consumption: {df_plot['Mean'].mean():.2f} Wh
   • Standard deviation: {df_plot['Mean'].std():.2f} Wh
   • Consumption range: {df_plot['Mean'].min():.2f} - {df_plot['Mean'].max():.2f} Wh
   • {len(outliers)} outliers detected ({len(outliers)/len(df)*100:.2f}%)

🏠 VARIABILITY INSIGHTS:
   • Peak hours consume {peak_consumption / off_peak_consumption:.2f}x more than off-peak
   • Weekday vs Weekend difference: {(weekly_data.iloc[:5].mean() - weekly_data.iloc[5:].mean()) / weekly_data.iloc[5:].mean() * 100:.1f}%
   • Daily variability (Max-Min): {(df_plot['Max'] - df_plot['Min']).mean():.2f} Wh
""")

print("\n" + "=" * 80)
print("✓ Analysis complete! Check generated PNG files for visualizations.")
print("=" * 80)
