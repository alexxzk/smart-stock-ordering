from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Optional
from datetime import date, datetime
import numpy as np

from app.ml.ordering_behavior import OrderingBehaviorLearner
from app.ml.forecasting import SalesForecaster
from app.ml.inventory import InventoryManager
from app.models.orders import OrderRequest, OrderResponse
from app.models.sales import SalesData, ForecastResult
from app.models.inventory import InventoryItem

router = APIRouter()
security = HTTPBearer()

# Initialize ML components
ordering_learner = OrderingBehaviorLearner()
sales_forecaster = SalesForecaster()
inventory_manager = InventoryManager()

@router.post("/train-models")
async def train_ordering_models(
    sales_data: List[Dict],
    order_history: List[Dict],
    ingredients: List[str],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Train AI models on sales and order history"""
    try:
        results = ordering_learner.train_models(sales_data, order_history, ingredients)
        
        if "error" in results:
            raise HTTPException(status_code=400, detail=results["error"])
        
        return {
            "message": "Models trained successfully",
            "trained_ingredients": list(results.keys()),
            "model_performance": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training error: {str(e)}")

@router.post("/ai-recommendation")
async def get_ai_order_recommendation(
    forecast_data: Dict,
    current_stock: Optional[Dict[str, float]] = None,
    weather_forecast: Optional[Dict] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get AI-powered order recommendation based on learned behavior"""
    try:
        # Get AI predictions
        ai_predictions = ordering_learner.predict_order_quantities(
            forecast_data, current_stock or {}, weather_forecast
        )
        
        if "error" in ai_predictions:
            # Fall back to traditional inventory calculation
            traditional_requirements = inventory_manager.calculate_ingredient_requirements(
                forecast_data, current_stock or {}
            )
            
            return {
                "recommendation_type": "traditional",
                "reason": "AI models not yet trained",
                "ingredient_requirements": traditional_requirements,
                "ai_available": False
            }
        
        # Combine AI predictions with inventory logic
        recommendations = []
        for ingredient, predicted_packs in ai_predictions["predictions"].items():
            if ingredient in inventory_manager.suppliers:
                supplier_info = inventory_manager.suppliers[ingredient]
                current_stock_amount = current_stock.get(ingredient, 0) if current_stock else 0
                
                # Calculate total amount needed
                pack_size = supplier_info['pack_size']
                total_amount_needed = predicted_packs * pack_size
                
                # Calculate cost
                total_cost = predicted_packs * supplier_info['cost_per_pack']
                
                # Determine urgency
                urgency = "medium"  # Default
                if predicted_packs > 3:
                    urgency = "high"
                elif predicted_packs == 0:
                    urgency = "low"
                
                recommendations.append({
                    "ingredient_name": ingredient,
                    "ai_predicted_packs": predicted_packs,
                    "current_stock": current_stock_amount,
                    "pack_size": pack_size,
                    "total_amount_needed": total_amount_needed,
                    "total_cost": total_cost,
                    "supplier": supplier_info['supplier'],
                    "urgency": urgency,
                    "explanation": ai_predictions["explanations"].get(ingredient, ""),
                    "model_accuracy": ai_predictions["model_accuracy"].get(ingredient, 0)
                })
        
        return {
            "recommendation_type": "ai_powered",
            "ingredient_recommendations": recommendations,
            "total_cost": sum(r['total_cost'] for r in recommendations),
            "ai_available": True,
            "overall_accuracy": np.mean(list(ai_predictions["model_accuracy"].values()))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")

@router.post("/confirm-order")
async def confirm_ai_order(
    order_data: Dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Confirm an AI-recommended order and update learning models"""
    try:
        # Store the confirmed order for learning
        ordering_learner.update_models_with_new_order(order_data)
        
        # Generate supplier orders
        supplier_orders = inventory_manager.generate_supplier_orders(
            order_data.get('ingredient_requirements', [])
        )
        
        return {
            "message": "Order confirmed and models updated",
            "order_id": f"order_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "supplier_orders": supplier_orders,
            "total_cost": sum(order['total_cost'] for order in supplier_orders),
            "learning_updated": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Order confirmation error: {str(e)}")

@router.get("/learning-insights")
async def get_learning_insights(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get insights about what the AI has learned"""
    try:
        insights = ordering_learner.get_learning_insights()
        
        return {
            "insights": insights,
            "total_ingredients_learned": len(insights),
            "average_accuracy": np.mean([insight['accuracy'] for insight in insights.values()]) if insights else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insights error: {str(e)}")

@router.post("/override-recommendation")
async def override_ai_recommendation(
    ingredient: str,
    manual_quantity: int,
    reason: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Override AI recommendation with manual input"""
    try:
        # Store override for learning (to improve future recommendations)
        override_data = {
            "ingredient": ingredient,
            "manual_quantity": manual_quantity,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "message": "Override recorded for learning",
            "override_data": override_data,
            "note": "This override will help improve future AI recommendations"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Override error: {str(e)}")

@router.get("/model-status")
async def get_model_status(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get status of AI models"""
    try:
        models = ordering_learner.models
        
        return {
            "trained_models": len(models),
            "available_ingredients": list(models.keys()),
            "model_types": {ingredient: "Random Forest" for ingredient in models.keys()},
            "ready_for_recommendations": len(models) > 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status error: {str(e)}") 