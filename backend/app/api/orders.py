from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Optional
from datetime import date, datetime

from app.ml.inventory import InventoryManager
from app.models.sales import SupplierOrder

router = APIRouter()
security = HTTPBearer()

# Initialize inventory manager
inventory_manager = InventoryManager()

@router.post("/generate")
async def generate_supplier_orders(
    ingredient_requirements: List[Dict],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Generate supplier orders from ingredient requirements"""
    try:
        orders = inventory_manager.generate_supplier_orders(ingredient_requirements)
        
        return {
            "supplier_orders": orders,
            "total_orders": len(orders),
            "total_cost": sum(order['total_cost'] for order in orders),
            "suppliers": list(set(order['supplier_name'] for order in orders))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Order generation error: {str(e)}")

@router.get("/history")
async def get_order_history(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get order history (demo data)"""
    # In a real app, this would come from the database
    demo_orders = [
        {
            "id": "order_001",
            "supplier_name": "Coffee Supply Co",
            "order_items": [
                {
                    "ingredient": "coffee_beans",
                    "packs_needed": 2,
                    "pack_size": 10,
                    "cost_per_pack": 120.0,
                    "total_cost": 240.0,
                    "urgency": "high"
                }
            ],
            "total_cost": 240.0,
            "delivery_date": "2024-01-15",
            "order_status": "confirmed",
            "created_at": "2024-01-10T10:30:00Z",
            "notes": "Regular weekly order"
        },
        {
            "id": "order_002",
            "supplier_name": "Dairy Fresh",
            "order_items": [
                {
                    "ingredient": "milk",
                    "packs_needed": 3,
                    "pack_size": 4,
                    "cost_per_pack": 8.0,
                    "total_cost": 24.0,
                    "urgency": "medium"
                },
                {
                    "ingredient": "cheese",
                    "packs_needed": 1,
                    "pack_size": 5,
                    "cost_per_pack": 35.0,
                    "total_cost": 35.0,
                    "urgency": "low"
                }
            ],
            "total_cost": 59.0,
            "delivery_date": "2024-01-12",
            "order_status": "delivered",
            "created_at": "2024-01-08T14:20:00Z",
            "notes": "Daily delivery"
        }
    ]
    
    return {
        "orders": demo_orders,
        "total_orders": len(demo_orders),
        "pending_orders": len([o for o in demo_orders if o['order_status'] == 'pending']),
        "delivered_orders": len([o for o in demo_orders if o['order_status'] == 'delivered'])
    }

@router.post("/create")
async def create_order(
    order_data: Dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a new supplier order"""
    try:
        # In a real app, this would save to the database
        order_id = f"order_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "order_id": order_id,
            "message": "Order created successfully",
            "order_data": order_data,
            "created_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Order creation error: {str(e)}")

@router.put("/{order_id}/status")
async def update_order_status(
    order_id: str,
    status: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update order status"""
    valid_statuses = ["pending", "confirmed", "delivered", "cancelled"]
    
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    try:
        # In a real app, this would update the database
        return {
            "order_id": order_id,
            "new_status": status,
            "message": "Order status updated successfully",
            "updated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status update error: {str(e)}")

@router.get("/analytics")
async def get_order_analytics(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get order analytics and insights"""
    # In a real app, this would calculate from actual data
    return {
        "total_spent_this_month": 1250.0,
        "average_order_value": 312.5,
        "most_ordered_ingredient": "coffee_beans",
        "top_supplier": "Dairy Fresh",
        "orders_this_month": 4,
        "delivery_on_time_rate": 0.95,
        "cost_savings_vs_last_month": 150.0,
        "urgent_orders_count": 2
    } 