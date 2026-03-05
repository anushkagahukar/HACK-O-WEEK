"""
K-Means Clustering Module
==========================
Applies K-Means clustering to identify High, Medium, and Low usage patterns.
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
from .utils import normalize_features

class EnergyClusterer:
    """
    Performs K-Means clustering on daily energy usage profiles.
    
    Attributes:
    -----------
    daily_data : DataFrame
        Input daily statistics
    features : array
        Extracted features for clustering
    kmeans_model : KMeans
        Fitted K-Means model
    labels : array
        Cluster labels for each day
    cluster_info : DataFrame
        Cluster characteristics
    """
    
    def __init__(self):
        """Initialize the clusterer."""
        self.daily_data = None
        self.features = None
        self.scaler = None
        self.kmeans_model = None
        self.labels = None
        self.cluster_info = None
        self.n_clusters = 3
    
    def prepare_features(self, daily_data):
        """
        Prepare features for clustering from daily data.
        
        Parameters:
        -----------
        daily_data : DataFrame
            Daily statistics with columns including Daily_Avg, Daily_Total
            
        Returns:
        --------
        array
            Feature matrix
        """
        
        # Select features for clustering
        # Using Daily_Avg and Daily_Total gives us information about both
        # the intensity and volume of consumption
        self.features = daily_data[['Daily_Avg', 'Daily_Total']].values
        
        # Standardize features (important for K-Means)
        self.scaler = StandardScaler()
        self.features = self.scaler.fit_transform(self.features)
        
        return self.features
    
    def fit(self, daily_data, n_clusters=3, random_state=42):
        """
        Fit K-Means clustering model.
        
        Parameters:
        -----------
        daily_data : DataFrame
            Daily statistics
        n_clusters : int
            Number of clusters (default: 3 for High, Medium, Low)
        random_state : int
            Random seed for reproducibility
        """
        
        self.daily_data = daily_data.copy()
        self.n_clusters = n_clusters
        
        # Prepare features
        self.prepare_features(self.daily_data)
        
        # Fit K-Means
        self.kmeans_model = KMeans(
            n_clusters=n_clusters,
            n_init=10,
            random_state=random_state,
            algorithm='lloyd'
        )
        
        self.labels = self.kmeans_model.fit_predict(self.features)
        
        # Add labels to data
        self.daily_data['Cluster'] = self.labels
        
        # Compute cluster characteristics
        self._compute_cluster_info()
        
        print(f"✓ Clustering completed!")
        print(f"  K-Means with {n_clusters} clusters")
        print(f"\nCluster Distribution:")
        self._print_cluster_distribution()
    
    def _compute_cluster_info(self):
        """Compute cluster characteristics."""
        
        cluster_stats = []
        
        # Map clusters to usage levels based on average consumption
        cluster_avgs = []
        for cluster_id in range(self.n_clusters):
            cluster_data = self.daily_data[self.daily_data['Cluster'] == cluster_id]
            avg_consumption = cluster_data['Daily_Avg'].mean()
            cluster_avgs.append((cluster_id, avg_consumption))
        
        # Sort by average consumption
        cluster_avgs.sort(key=lambda x: x[1])
        
        # Assign labels: Low, Medium, High
        usage_levels = ['Low', 'Medium', 'High']
        cluster_mapping = {old_id: usage_levels[i] for i, (old_id, _) in enumerate(cluster_avgs)}
        
        # Map back to original cluster IDs
        for original_cluster_id, level in cluster_mapping.items():
            cluster_data = self.daily_data[self.daily_data['Cluster'] == original_cluster_id]
            
            cluster_stats.append({
                'Cluster_ID': original_cluster_id,
                'Usage_Level': level,
                'Count': len(cluster_data),
                'Avg_Daily_Consumption': round(cluster_data['Daily_Avg'].mean(), 2),
                'Total_Daily_Consumption': round(cluster_data['Daily_Total'].mean(), 2),
                'Min_Daily_Consumption': round(cluster_data['Daily_Avg'].min(), 2),
                'Max_Daily_Consumption': round(cluster_data['Daily_Avg'].max(), 2),
                'Weekday_Count': len(cluster_data[cluster_data['Day_Type'] == 'Weekday']),
                'Weekend_Count': len(cluster_data[cluster_data['Day_Type'] == 'Weekend'])
            })
        
        self.cluster_info = pd.DataFrame(cluster_stats)
        
        # Update daily_data with usage levels
        usage_level_map = {}
        for _, row in self.cluster_info.iterrows():
            usage_level_map[row['Cluster_ID']] = row['Usage_Level']
        
        self.daily_data['Usage_Level'] = self.daily_data['Cluster'].map(usage_level_map)
    
    def _print_cluster_distribution(self):
        """Print cluster distribution."""
        for _, row in self.cluster_info.iterrows():
            pct = (row['Count'] / len(self.daily_data)) * 100
            print(f"  {row['Usage_Level']:8} (Cluster {int(row['Cluster_ID'])}) - {int(row['Count']):3} days ({pct:5.1f}%)")
    
    def get_cluster_info(self):
        """
        Get cluster information.
        
        Returns:
        --------
        DataFrame
            Cluster characteristics and statistics
        """
        return self.cluster_info.copy()
    
    def get_labeled_data(self):
        """
        Get daily data with cluster labels.
        
        Returns:
        --------
        DataFrame
            Daily data with Cluster and Usage_Level columns
        """
        return self.daily_data.copy()
    
    def visualize_clusters(self, figsize=(12, 7)):
        """
        Visualize clustering results with scatter plot.
        
        Parameters:
        -----------
        figsize : tuple
            Figure size (width, height)
        """
        
        if self.daily_data is None:
            raise RuntimeError("Model not fitted. Call fit() first.")
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Define colors for each usage level
        color_map = {'Low': '#2ecc71', 'Medium': '#f39c12', 'High': '#e74c3c'}
        
        # Plot points for each cluster
        for usage_level in ['Low', 'Medium', 'High']:
            mask = self.daily_data['Usage_Level'] == usage_level
            cluster_data = self.daily_data[mask]
            
            # Color differently for weekday vs weekend
            weekday_mask = cluster_data['Day_Type'] == 'Weekday'
            
            # Weekdays - solid dots
            ax.scatter(
                cluster_data[weekday_mask]['Daily_Avg'],
                cluster_data[weekday_mask]['Daily_Total'],
                c=color_map[usage_level],
                s=80,
                alpha=0.7,
                marker='o',
                label=f'{usage_level} (Weekday)',
                edgecolors='black',
                linewidth=0.5
            )
            
            # Weekends - different marker
            ax.scatter(
                cluster_data[~weekday_mask]['Daily_Avg'],
                cluster_data[~weekday_mask]['Daily_Total'],
                c=color_map[usage_level],
                s=80,
                alpha=0.7,
                marker='s',
                label=f'{usage_level} (Weekend)',
                edgecolors='black',
                linewidth=0.5
            )
        
        # Plot cluster centers
        centers = self.scaler.inverse_transform(self.kmeans_model.cluster_centers_)
        ax.scatter(
            centers[:, 0],
            centers[:, 1],
            c='red',
            s=300,
            alpha=0.8,
            marker='*',
            edgecolors='darkred',
            linewidth=2,
            label='Cluster Centers',
            zorder=5
        )
        
        # Labels and title
        ax.set_xlabel('Daily Average Consumption (kWh)', fontsize=12, fontweight='bold', color='#000000')
        ax.set_ylabel('Daily Total Consumption (kWh)', fontsize=12, fontweight='bold', color='#000000')
        ax.set_title('K-Means Clustering of Daily Energy Usage Profiles', 
                    fontsize=14, fontweight='bold', pad=20, color='#000000')
        ax.tick_params(colors='#000000')
        
        # Legend
        ax.legend(loc='best', fontsize=10, framealpha=0.95)
        
        # Grid
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Layout
        plt.tight_layout()
        
        return fig
    
    def print_cluster_summary(self):
        """Print cluster summary statistics."""
        if self.cluster_info is None:
            raise RuntimeError("Model not fitted. Call fit() first.")
        
        print("\n" + "="*80)
        print("CLUSTERING RESULTS SUMMARY")
        print("="*80)
        print(self.cluster_info.to_string(index=False))
        print("="*80 + "\n")
