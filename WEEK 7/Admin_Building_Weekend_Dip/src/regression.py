"""
Regression and Forecasting Module
==================================
Uses Linear and Polynomial regression to forecast future energy usage.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings('ignore')

class EnergyRegressor:
    """
    Performs regression analysis and forecasting for each cluster.
    
    Attributes:
    -----------
    models : dict
        Fitted regression models for each cluster
    forecasts : dict
        Forecast results for each cluster
    metrics : dict
        Performance metrics for each model
    """
    
    def __init__(self):
        """Initialize the regressor."""
        self.models = {}
        self.forecasts = {}
        self.metrics = {}
        self.scaled_X = {}
        self.original_X_range = None
    
    def prepare_training_data(self, daily_data):
        """
        Prepare sequential data for regression.
        
        Parameters:
        -----------
        daily_data : DataFrame
            Daily statistics with Cluster/Usage_Level column
            
        Returns:
        --------
        dict
            Training data for each cluster with X (day index) and y (consumption)
        """
        
        training_data = {}
        
        # Get unique clusters/usage levels
        clusters = daily_data['Usage_Level'].unique()
        
        for cluster in clusters:
            cluster_data = daily_data[daily_data['Usage_Level'] == cluster].copy()
            
            # Reset index to create sequential day numbers
            cluster_data = cluster_data.reset_index(drop=True)
            
            # Create day index as feature (X)
            X = np.arange(len(cluster_data)).reshape(-1, 1)
            
            # Target variable (y)
            y = cluster_data['Daily_Avg'].values
            
            training_data[cluster] = {
                'X': X,
                'y': y,
                'dates': cluster_data['Date'].values,
                'raw_data': cluster_data
            }
        
        self.original_X_range = {'max': max([d['X'].max() for d in training_data.values()])}
        
        return training_data
    
    def _scale_X(self, X):
        """Normalize X values for better numerical stability."""
        X_min = X.min()
        X_max = X.max()
        X_range = X_max - X_min if X_max > X_min else 1
        return (X - X_min) / X_range, {'min': X_min, 'max': X_max, 'range': X_range}
    
    def fit(self, daily_data, degree=2):
        """
        Fit polynomial regression models for each cluster.
        
        Parameters:
        -----------
        daily_data : DataFrame
            Daily statistics with cluster labels
        degree : int
            Polynomial degree (1 for linear, 2+ for polynomial)
        """
        
        # Prepare training data
        training_data = self.prepare_training_data(daily_data)
        
        print(f"✓ Fitting regression models (degree={degree})...")
        
        # Fit model for each cluster
        for cluster, data in training_data.items():
            X = data['X']
            y = data['y']
            
            # Scale X
            X_scaled, scale_params = self._scale_X(X)
            self.scaled_X[cluster] = scale_params
            
            # Create polynomial features if degree > 1
            if degree > 1:
                poly_features = PolynomialFeatures(degree=degree)
                X_poly = poly_features.fit_transform(X_scaled)
            else:
                X_poly = X_scaled
            
            # Fit linear regression on polynomial features
            model = LinearRegression()
            model.fit(X_poly, y)
            
            # Store model and preprocessing pipeline
            self.models[cluster] = {
                'model': model,
                'degree': degree,
                'poly_features': poly_features if degree > 1 else None,
                'scale_params': scale_params
            }
            
            # Calculate training metrics
            y_pred = model.predict(X_poly)
            mse = mean_squared_error(y, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y, y_pred)
            r2 = r2_score(y, y_pred)
            
            self.metrics[cluster] = {
                'mse': round(mse, 4),
                'rmse': round(rmse, 4),
                'mae': round(mae, 4),
                'r2_score': round(r2, 4),
                'training_samples': len(y)
            }
            
            print(f"  {cluster:8} - R²={r2:.4f}, RMSE={rmse:.2f} kWh, MAE={mae:.2f} kWh")
    
    def forecast(self, days_into_future=30):
        """
        Generate forecasts for specified days into the future.
        
        Parameters:
        -----------
        days_into_future : int
            Number of days to forecast (default: 30)
        """
        
        if not self.models:
            raise RuntimeError("Model not fitted. Call fit() first.")
        
        self.forecasts = {}
        
        for cluster, model_info in self.models.items():
            model = model_info['model']
            degree = model_info['degree']
            scale_params = model_info['scale_params']
            poly_features = model_info['poly_features']
            
            # Create future time points
            last_X = self.original_X_range['max']
            future_X = np.arange(last_X + 1, last_X + days_into_future + 1).reshape(-1, 1)
            
            # Scale future X
            X_min = scale_params['min']
            X_range = scale_params['range']
            future_X_scaled = (future_X - X_min) / X_range
            
            # Create polynomial features
            if degree > 1:
                future_X_poly = poly_features.transform(future_X_scaled)
            else:
                future_X_poly = future_X_scaled
            
            # Make predictions
            predictions = model.predict(future_X_poly)
            
            # Ensure non-negative predictions
            predictions = np.maximum(predictions, 0)
            
            self.forecasts[cluster] = {
                'days': np.arange(1, days_into_future + 1),
                'forecasted_usage': predictions,
                'mean_forecast': round(predictions.mean(), 2),
                'trend': 'increasing' if predictions[-1] > predictions[0] else 'decreasing'
            }
        
        print(f"✓ Generated forecasts for {days_into_future} days into the future.")
    
    def get_forecasts(self):
        """
        Get forecast results.
        
        Returns:
        --------
        dict
            Forecasts for each cluster
        """
        return self.forecasts
    
    def get_metrics(self):
        """
        Get model performance metrics.
        
        Returns:
        --------
        dict
            Performance metrics for each cluster
        """
        return self.metrics
    
    def visualize_forecasts(self, daily_data, figsize=(14, 8)):
        """
        Visualize actual data and forecasts.
        
        Parameters:
        -----------
        daily_data : DataFrame
            Daily data with cluster labels
        figsize : tuple
            Figure size
        """
        
        if not self.forecasts:
            raise RuntimeError("No forecasts available. Call forecast() first.")
        
        clusters = list(self.forecasts.keys())
        n_clusters = len(clusters)
        
        fig, axes = plt.subplots(n_clusters, 1, figsize=figsize)
        
        if n_clusters == 1:
            axes = [axes]
        
        colors = {'Low': '#2ecc71', 'Medium': '#f39c12', 'High': '#e74c3c'}
        
        for idx, cluster in enumerate(clusters):
            ax = axes[idx]
            
            # Get historical data
            cluster_data = daily_data[daily_data['Usage_Level'] == cluster]
            historical_days = np.arange(len(cluster_data))
            historical_usage = cluster_data['Daily_Avg'].values
            
            # Get forecast
            forecast_data = self.forecasts[cluster]
            forecast_days = len(cluster_data) + forecast_data['days']
            forecast_usage = forecast_data['forecasted_usage']
            
            # Plot historical data
            ax.plot(historical_days, historical_usage, 'o-', 
                   color=colors[cluster], linewidth=2, markersize=4,
                   label='Historical Data', alpha=0.7)
            
            # Plot forecast
            ax.plot(forecast_days, forecast_usage, 's--', 
                   color=colors[cluster], linewidth=2, markersize=4,
                   label='Forecast', alpha=0.7)
            
            # Add vertical line to separate historical and forecast
            ax.axvline(x=len(cluster_data)-0.5, color='gray', linestyle=':', alpha=0.5)
            
            # Labels and styling
            ax.set_xlabel('Days', fontsize=10, color='#000000', fontweight='bold')
            ax.set_ylabel('Daily Avg Consumption (kWh)', fontsize=10, color='#000000', fontweight='bold')
            ax.set_title(f'{cluster} Usage Cluster - Historical & Forecast', 
                        fontsize=11, fontweight='bold', color='#000000')
            ax.tick_params(colors='#000000')
            ax.legend(loc='best', fontsize=9)
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def print_forecast_summary(self):
        """Print forecast summary."""
        if not self.forecasts:
            raise RuntimeError("No forecasts available. Call forecast() first.")
        
        print("\n" + "="*70)
        print("REGRESSION & FORECAST SUMMARY")
        print("="*70)
        
        for cluster, metrics in self.metrics.items():
            print(f"\n{cluster} Cluster:")
            print(f"  Training Samples:               {metrics['training_samples']}")
            print(f"  R² Score:                       {metrics['r2_score']:.4f}")
            print(f"  Root Mean Squared Error (RMSE): {metrics['rmse']:.4f} kWh")
            print(f"  Mean Absolute Error (MAE):      {metrics['mae']:.4f} kWh")
            print(f"\nForecast (next 30 days):")
            forecast = self.forecasts[cluster]
            print(f"  Mean Forecasted Usage:          {forecast['mean_forecast']:.2f} kWh")
            print(f"  Trend:                          {forecast['trend']}")
        
        print("\n" + "="*70 + "\n")
