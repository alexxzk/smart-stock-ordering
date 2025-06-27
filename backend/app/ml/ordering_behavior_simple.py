"""
Simplified Ordering Behavior Learning Module
Uses basic statistical methods for deployment compatibility
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class SimpleOrderingBehaviorLearner:
    """Simplified ordering behavior learner using basic statistical methods"""
    
    def __init__(self):
        self.sales_patterns = {}
        self.order_patterns = {}
        self.learning_data = []
        
    def learn_from_data(self, sales_data: List[Dict], order_data: List[Dict], 
                       weather_data: Optional[List[Dict]] = None) -> Dict:
        """Learn ordering patterns from historical data"""
        try:
            if not sales_data or not order_data:
                return {"error": "Insufficient data for learning"}
            
            # Store learning data
            self.learning_data = {
                'sales': sales_data,
                'orders': order_data,
                'weather': weather_data or []
            }
            
            # Analyze sales patterns
            sales_df = pd.DataFrame(sales_data)
            if not sales_df.empty and 'item_name' in sales_df.columns:
                self.sales_patterns = self._analyze_sales_patterns(sales_df)
            
            # Analyze order patterns
            orders_df = pd.DataFrame(order_data)
            if not orders_df.empty and 'item_name' in orders_df.columns:
                self.order_patterns = self._analyze_order_patterns(orders_df)
            
            return {
                'status': 'success',
                'sales_patterns_learned': len(self.sales_patterns),
                'order_patterns_learned': len(self.order_patterns),
                'total_records': len(sales_data) + len(order_data)
            }
            
        except Exception as e:
            logger.error(f"Error in learning: {e}")
            return {"error": f"Learning failed: {str(e)}"}
    
    def _analyze_sales_patterns(self, sales_df: pd.DataFrame) -> Dict:
        """Analyze sales patterns for each item"""
        patterns = {}
        
        try:
            for item in sales_df['item_name'].unique():
                item_data = sales_df[sales_df['item_name'] == item]
                
                patterns[item] = {
                    'avg_daily_sales': item_data['quantity'].mean() if 'quantity' in item_data.columns else 0,
                    'max_daily_sales': item_data['quantity'].max() if 'quantity' in item_data.columns else 0,
                    'min_daily_sales': item_data['quantity'].min() if 'quantity' in item_data.columns else 0,
                    'total_sales': item_data['quantity'].sum() if 'quantity' in item_data.columns else 0,
                    'sales_count': len(item_data)
                }
        except Exception as e:
            logger.error(f"Error analyzing sales patterns: {e}")
        
        return patterns
    
    def _analyze_order_patterns(self, orders_df: pd.DataFrame) -> Dict:
        """Analyze order patterns for each item"""
        patterns = {}
        
        try:
            for item in orders_df['item_name'].unique():
                item_data = orders_df[orders_df['item_name'] == item]
                
                patterns[item] = {
                    'avg_order_quantity': item_data['quantity'].mean() if 'quantity' in item_data.columns else 0,
                    'max_order_quantity': item_data['quantity'].max() if 'quantity' in item_data.columns else 0,
                    'min_order_quantity': item_data['quantity'].min() if 'quantity' in item_data.columns else 0,
                    'total_ordered': item_data['quantity'].sum() if 'quantity' in item_data.columns else 0,
                    'order_count': len(item_data)
                }
        except Exception as e:
            logger.error(f"Error analyzing order patterns: {e}")
        
        return patterns
    
    def predict_order_quantities(self, sales_forecast: Dict, 
                               current_inventory: Dict,
                               supplier_constraints: Optional[Dict] = None) -> Dict:
        """Predict optimal order quantities based on learned patterns"""
        try:
            recommendations = {}
            
            for item, forecast_data in sales_forecast.get('forecasts', {}).items():
                # Get forecasted daily average
                forecast_values = forecast_data.get('values', [])
                avg_forecast = sum(forecast_values) / len(forecast_values) if forecast_values else 0
                
                # Get current inventory
                current_stock = current_inventory.get(item, 0)
                
                # Get learned patterns
                sales_pattern = self.sales_patterns.get(item, {})
                order_pattern = self.order_patterns.get(item, {})
                
                # Calculate recommended order quantity
                # Basic formula: (forecast * days) - current_stock + safety_stock
                days_to_cover = 7  # Order for 7 days
                safety_stock = avg_forecast * 2  # 2 days safety stock
                
                recommended_quantity = max(0, (avg_forecast * days_to_cover) - current_stock + safety_stock)
                
                # Apply supplier constraints if available
                if supplier_constraints and item in supplier_constraints:
                    min_order = supplier_constraints[item].get('min_order', 0)
                    pack_size = supplier_constraints[item].get('pack_size', 1)
                    
                    # Round up to minimum order and pack size
                    recommended_quantity = max(min_order, recommended_quantity)
                    recommended_quantity = ((recommended_quantity + pack_size - 1) // pack_size) * pack_size
                
                recommendations[item] = {
                    'recommended_quantity': round(recommended_quantity, 2),
                    'current_stock': current_stock,
                    'forecasted_daily_avg': round(avg_forecast, 2),
                    'days_to_cover': days_to_cover,
                    'safety_stock': round(safety_stock, 2),
                    'confidence_score': 0.85,  # Default confidence
                    'reasoning': f"Based on {len(forecast_values)} days of forecast data"
                }
            
            return {
                'recommendations': recommendations,
                'total_items': len(recommendations),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            return {"error": f"Prediction failed: {str(e)}"}
    
    def update_patterns(self, new_sales_data: List[Dict], new_order_data: List[Dict]) -> Dict:
        """Update learned patterns with new data"""
        try:
            # Combine new data with existing learning data
            if self.learning_data:
                self.learning_data['sales'].extend(new_sales_data)
                self.learning_data['orders'].extend(new_order_data)
            else:
                self.learning_data = {
                    'sales': new_sales_data,
                    'orders': new_order_data,
                    'weather': []
                }
            
            # Re-learn patterns with updated data
            return self.learn_from_data(
                self.learning_data['sales'],
                self.learning_data['orders'],
                self.learning_data.get('weather', [])
            )
            
        except Exception as e:
            logger.error(f"Error updating patterns: {e}")
            return {"error": f"Update failed: {str(e)}"}
    
    def get_patterns_summary(self) -> Dict:
        """Get summary of learned patterns"""
        try:
            return {
                'sales_patterns': {
                    'total_items': len(self.sales_patterns),
                    'items': list(self.sales_patterns.keys())
                },
                'order_patterns': {
                    'total_items': len(self.order_patterns),
                    'items': list(self.order_patterns.keys())
                },
                'learning_data': {
                    'sales_records': len(self.learning_data.get('sales', [])),
                    'order_records': len(self.learning_data.get('orders', [])),
                    'weather_records': len(self.learning_data.get('weather', []))
                },
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting patterns summary: {e}")
            return {"error": f"Failed to get patterns: {str(e)}"} 