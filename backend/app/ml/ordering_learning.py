import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

class OrderingBehaviorLearner:
    """AI-powered ordering behavior learning system"""
    
    def __init__(self):
        self.models = {}  # One model per ingredient
        self.weather_cache = {}
        self.feature_columns = [
            'day_of_week', 'month', 'quarter', 'is_weekend', 'is_holiday',
            'temperature', 'precipitation', 'humidity', 'sales_amount',
            'orders_count', 'days_since_last_order', 'season'
        ]
        
    def fetch_weather_data(self, date_obj: date, location: str = "London,UK") -> Dict:
        """Fetch weather data for a specific date (using OpenWeatherMap API)"""
        # For demo purposes, return mock weather data
        # In production, you'd use: https://api.openweathermap.org/data/2.5/weather
        cache_key = f"{date_obj}_{location}"
        
        if cache_key in self.weather_cache:
            return self.weather_cache[cache_key]
        
        # Mock weather data based on season
        month = date_obj.month
        if month in [12, 1, 2]:  # Winter
            weather = {"temperature": 5, "precipitation": 0.3, "humidity": 80}
        elif month in [3, 4, 5]:  # Spring
            weather = {"temperature": 15, "precipitation": 0.2, "humidity": 70}
        elif month in [6, 7, 8]:  # Summer
            weather = {"temperature": 25, "precipitation": 0.1, "humidity": 60}
        else:  # Fall
            weather = {"temperature": 12, "precipitation": 0.4, "humidity": 75}
        
        self.weather_cache[cache_key] = weather
        return weather
    
    def prepare_features(self, sales_data: List[Dict], order_history: List[Dict]) -> pd.DataFrame:
        """Prepare features for ML model training"""
        # Combine sales and order data
        combined_data = []
        
        for sale in sales_data:
            sale_date = pd.to_datetime(sale['date']).date()
            weather = self.fetch_weather_data(sale_date)
            
            # Find corresponding order data
            order_data = next((o for o in order_history if o['date'] == sale['date']), {})
            
            # Calculate days since last order
            days_since_last_order = 1  # Default
            if order_history:
                last_order_date = max([pd.to_datetime(o['date']).date() for o in order_history])
                days_since_last_order = (sale_date - last_order_date).days
            
            features = {
                'date': sale_date,
                'day_of_week': sale_date.weekday(),
                'month': sale_date.month,
                'quarter': (sale_date.month - 1) // 3 + 1,
                'is_weekend': 1 if sale_date.weekday() >= 5 else 0,
                'is_holiday': 0,  # Could be enhanced with holiday calendar
                'temperature': weather['temperature'],
                'precipitation': weather['precipitation'],
                'humidity': weather['humidity'],
                'sales_amount': sale['sales_amount'],
                'orders_count': sale['orders_count'],
                'days_since_last_order': days_since_last_order,
                'season': (sale_date.month % 12 + 3) // 3
            }
            
            # Add order quantities for each ingredient
            if order_data:
                for item in order_data.get('order_items', []):
                    ingredient = item['ingredient']
                    features[f'order_{ingredient}'] = item['packs_needed']
            
            combined_data.append(features)
        
        return pd.DataFrame(combined_data)
    
    def train_models(self, sales_data: List[Dict], order_history: List[Dict], 
                    ingredients: List[str]) -> Dict:
        """Train ML models for each ingredient"""
        if not sales_data or not order_history:
            return {"error": "Insufficient data for training"}
        
        # Prepare features
        df = self.prepare_features(sales_data, order_history)
        
        # Train model for each ingredient
        model_results = {}
        
        for ingredient in ingredients:
            target_col = f'order_{ingredient}'
            
            if target_col not in df.columns:
                # No order data for this ingredient, skip
                continue
            
            # Prepare features and target
            feature_cols = [col for col in self.feature_columns if col in df.columns]
            X = df[feature_cols].fillna(0)
            y = df[target_col].fillna(0)
            
            if len(X) < 10:
                continue  # Need more data
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Train model
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Store model and results
            self.models[ingredient] = {
                'model': model,
                'feature_columns': feature_cols,
                'mae': mae,
                'r2': r2,
                'feature_importance': dict(zip(feature_cols, model.feature_importances_))
            }
            
            model_results[ingredient] = {
                'mae': mae,
                'r2': r2,
                'feature_importance': dict(zip(feature_cols, model.feature_importances_))
            }
        
        return model_results
    
    def predict_order_quantities(self, forecast_data: Dict, current_stock: Dict[str, float],
                               weather_forecast: Optional[Dict] = None) -> Dict:
        """Predict order quantities based on learned behavior"""
        if not self.models:
            return {"error": "No trained models available"}
        
        predictions = {}
        explanations = {}
        
        for ingredient, model_info in self.models.items():
            model = model_info['model']
            feature_cols = model_info['feature_columns']
            
            # Prepare features for prediction
            features = {}
            
            # Use the first forecast date as reference
            forecast_date = pd.to_datetime(forecast_data['dates'][0]).date()
            weather = weather_forecast or self.fetch_weather_data(forecast_date)
            
            # Basic features
            features['day_of_week'] = forecast_date.weekday()
            features['month'] = forecast_date.month
            features['quarter'] = (forecast_date.month - 1) // 3 + 1
            features['is_weekend'] = 1 if forecast_date.weekday() >= 5 else 0
            features['is_holiday'] = 0
            features['temperature'] = weather['temperature']
            features['precipitation'] = weather['precipitation']
            features['humidity'] = weather['humidity']
            features['season'] = (forecast_date.month % 12 + 3) // 3
            
            # Sales features (use average from forecast)
            features['sales_amount'] = np.mean(forecast_data['predicted_sales'])
            features['orders_count'] = np.mean(forecast_data['predicted_orders'])
            features['days_since_last_order'] = 7  # Assume weekly ordering
            
            # Create feature vector
            X = pd.DataFrame([features])
            X = X[feature_cols].fillna(0)
            
            # Make prediction
            predicted_packs = model.predict(X)[0]
            predicted_packs = max(0, round(predicted_packs))  # Ensure non-negative
            
            predictions[ingredient] = predicted_packs
            
            # Generate explanation
            importance = model_info['feature_importance']
            top_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:3]
            
            explanation = f"Based on your ordering patterns, particularly on {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][features['day_of_week']]}s"
            if features['is_weekend']:
                explanation += " (weekends)"
            explanation += f" and {['winter', 'spring', 'summer', 'fall'][features['season']-1]} weather conditions"
            
            explanations[ingredient] = explanation
        
        return {
            "predictions": predictions,
            "explanations": explanations,
            "model_accuracy": {ingredient: info['r2'] for ingredient, info in self.models.items()}
        }
    
    def update_models_with_new_order(self, order_data: Dict):
        """Update models with new order data (for continuous learning)"""
        # This would be called when a new order is placed
        # For now, we'll just store the data for retraining
        pass
    
    def get_learning_insights(self) -> Dict:
        """Get insights about what the AI has learned"""
        insights = {}
        
        for ingredient, model_info in self.models.items():
            importance = model_info['feature_importance']
            top_factors = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:3]
            
            insights[ingredient] = {
                "accuracy": model_info['r2'],
                "top_factors": top_factors,
                "model_type": "Random Forest"
            }
        
        return insights 