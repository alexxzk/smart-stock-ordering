"""
Simplified Sales Forecasting Module
Uses basic statistical methods instead of scikit-learn for deployment compatibility
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class SalesForecaster:
    """Simplified sales forecaster using basic statistical methods"""
    
    def __init__(self):
        self.sales_data = None
        self.forecast_data = None
        
    def load_data(self, csv_file_path: str) -> bool:
        """Load sales data from CSV file"""
        try:
            self.sales_data = pd.read_csv(csv_file_path)
            logger.info(f"Loaded {len(self.sales_data)} sales records")
            return True
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return False
    
    def prepare_data(self) -> bool:
        """Prepare data for forecasting"""
        if self.sales_data is None:
            logger.error("No sales data loaded")
            return False
            
        try:
            # Ensure we have required columns
            required_cols = ['date', 'quantity', 'item_name']
            missing_cols = [col for col in required_cols if col not in self.sales_data.columns]
            
            if missing_cols:
                logger.error(f"Missing required columns: {missing_cols}")
                return False
            
            # Convert date column
            self.sales_data['date'] = pd.to_datetime(self.sales_data['date'])
            
            # Aggregate by date and item
            daily_sales = self.sales_data.groupby(['date', 'item_name'])['quantity'].sum().reset_index()
            
            # Pivot to get items as columns
            self.sales_data = daily_sales.pivot(index='date', columns='item_name', values='quantity').fillna(0)
            
            logger.info(f"Prepared data with {len(self.sales_data)} days and {len(self.sales_data.columns)} items")
            return True
            
        except Exception as e:
            logger.error(f"Error preparing data: {e}")
            return False
    
    def simple_moving_average(self, data: pd.Series, window: int = 7) -> pd.Series:
        """Calculate simple moving average"""
        return data.rolling(window=window, min_periods=1).mean()
    
    def exponential_smoothing(self, data: pd.Series, alpha: float = 0.3) -> pd.Series:
        """Calculate exponential smoothing"""
        smoothed = pd.Series(index=data.index, dtype=float)
        smoothed.iloc[0] = data.iloc[0]
        
        for i in range(1, len(data)):
            smoothed.iloc[i] = alpha * data.iloc[i-1] + (1 - alpha) * smoothed.iloc[i-1]
        
        return smoothed
    
    def forecast_sales(self, days_ahead: int = 30, method: str = 'moving_average') -> Dict:
        """Forecast sales for the next N days"""
        if self.sales_data is None:
            return {"error": "No data prepared for forecasting"}
        
        try:
            forecasts = {}
            last_date = self.sales_data.index.max()
            
            for item in self.sales_data.columns:
                item_data = self.sales_data[item]
                
                if method == 'moving_average':
                    # Use last 7 days average
                    avg_daily = item_data.tail(7).mean()
                    forecast_values = [avg_daily] * days_ahead
                elif method == 'exponential_smoothing':
                    # Use exponential smoothing
                    smoothed = self.exponential_smoothing(item_data)
                    trend = (smoothed.iloc[-1] - smoothed.iloc[-7]) / 7 if len(smoothed) >= 7 else 0
                    forecast_values = [smoothed.iloc[-1] + trend * i for i in range(1, days_ahead + 1)]
                else:
                    # Simple average
                    avg_daily = item_data.mean()
                    forecast_values = [avg_daily] * days_ahead
                
                # Generate future dates
                future_dates = [last_date + timedelta(days=i+1) for i in range(days_ahead)]
                
                forecasts[item] = {
                    'dates': [d.strftime('%Y-%m-%d') for d in future_dates],
                    'values': [max(0, round(v, 2)) for v in forecast_values],
                    'method': method
                }
            
            return {
                'forecasts': forecasts,
                'method': method,
                'days_ahead': days_ahead,
                'total_items': len(forecasts)
            }
            
        except Exception as e:
            logger.error(f"Error in forecasting: {e}")
            return {"error": f"Forecasting failed: {str(e)}"}
    
    def get_forecast_summary(self) -> Dict:
        """Get a summary of the forecast"""
        if not self.forecast_data:
            return {"error": "No forecast data available"}
        
        try:
            summary = {
                'total_items': len(self.forecast_data.get('forecasts', {})),
                'forecast_period': self.forecast_data.get('days_ahead', 0),
                'method': self.forecast_data.get('method', 'unknown'),
                'items': []
            }
            
            for item, data in self.forecast_data.get('forecasts', {}).items():
                values = data.get('values', [])
                summary['items'].append({
                    'item_name': item,
                    'total_forecast': sum(values),
                    'avg_daily': sum(values) / len(values) if values else 0,
                    'max_daily': max(values) if values else 0,
                    'min_daily': min(values) if values else 0
                })
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting forecast summary: {e}")
            return {"error": f"Summary generation failed: {str(e)}"}

# Global instance for API use
forecaster = SalesForecaster() 