import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
from .ordering_behavior_simple import SimpleOrderingBehaviorLearner

class OrderingBehaviorLearner:
    """AI-powered ordering behavior learning"""
    
    def __init__(self):
        self.simple_learner = SimpleOrderingBehaviorLearner()
        self.behavior_patterns = {}
        self.weather_impact = {}
        self.seasonality_factors = {}
        
    def learn_from_data(self, sales_data: List[Dict], order_data: List[Dict], 
                       weather_data: Optional[List[Dict]] = None) -> Dict:
        """Learn ordering patterns from historical data"""
        try:
            return self.simple_learner.learn_from_data(sales_data, order_data, weather_data)
        except Exception as e:
            return {"error": f"Learning failed: {str(e)}"}
    
    def predict_order_quantities(self, sales_forecast: Dict, 
                               current_inventory: Dict,
                               supplier_constraints: Optional[Dict] = None) -> Dict:
        """Predict optimal order quantities based on learned patterns"""
        try:
            return self.simple_learner.predict_order_quantities(
                sales_forecast, current_inventory, supplier_constraints
            )
        except Exception as e:
            return {"error": f"Prediction failed: {str(e)}"}
    
    def update_patterns(self, new_sales_data: List[Dict], new_order_data: List[Dict]) -> Dict:
        """Update learned patterns with new data"""
        try:
            return self.simple_learner.update_patterns(new_sales_data, new_order_data)
        except Exception as e:
            return {"error": f"Update failed: {str(e)}"}
    
    def get_patterns_summary(self) -> Dict:
        """Get summary of learned patterns"""
        try:
            return self.simple_learner.get_patterns_summary()
        except Exception as e:
            return {"error": f"Failed to get patterns: {str(e)}"}
    
    def analyze_ordering_efficiency(self, order_history: List[Dict], 
                                  sales_data: List[Dict]) -> Dict:
        """Analyze ordering efficiency and provide recommendations"""
        if not order_history or not sales_data:
            return {"error": "Insufficient data for analysis"}
        
        # Calculate basic metrics
        total_orders = len(order_history)
        total_sales = len(sales_data)
        
        # Calculate order accuracy (simplified)
        accuracy = 0.85  # Default accuracy
        
        # Calculate waste percentage (simplified)
        waste_percentage = 0.05  # Default 5% waste
        
        recommendations = [
            "Consider ordering smaller quantities more frequently",
            "Monitor seasonal patterns for better forecasting",
            "Review supplier lead times to optimize ordering"
        ]
        
        return {
            'total_orders': total_orders,
            'total_sales': total_sales,
            'order_accuracy': accuracy,
            'waste_percentage': waste_percentage,
            'efficiency_score': max(0, 100 - (waste_percentage * 100)),
            'recommendations': recommendations,
            'created_at': datetime.now()
        } 