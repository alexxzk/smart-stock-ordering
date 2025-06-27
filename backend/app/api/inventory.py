from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Optional
from datetime import date, datetime
from pydantic import BaseModel
import time
import logging

from app.ml.inventory import InventoryManager
from app.models.sales import IngredientRequirement
from app.firebase_init import get_firestore_client
from app.cache_redis import cached, invalidate_cache

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

# Initialize inventory manager
inventory_manager = InventoryManager()

# Pydantic models
class InventoryItemBase(BaseModel):
    name: str
    category: str
    currentStock: float
    minStock: float
    maxStock: float
    unit: str
    costPerUnit: float
    supplierId: str

class InventoryItemCreate(InventoryItemBase):
    pass

class InventoryItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    currentStock: Optional[float] = None
    minStock: Optional[float] = None
    maxStock: Optional[float] = None
    unit: Optional[str] = None
    costPerUnit: Optional[float] = None
    supplierId: Optional[str] = None

class StockUpdate(BaseModel):
    newStock: float
    reason: Optional[str] = None

class InventoryItemResponse(InventoryItemBase):
    id: str
    userId: str
    lastUpdated: datetime

# Performance monitoring
def log_performance(operation: str, duration: float, details: str = ""):
    """Log performance metrics"""
    logger.info(f"[PERF] {operation} took {duration:.3f}s {details}")

@router.post("/calculate-requirements")
async def calculate_ingredient_requirements(
    forecast_data: Dict,
    current_stock: Optional[Dict[str, float]] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Calculate ingredient requirements based on sales forecast"""
    try:
        requirements = inventory_manager.calculate_ingredient_requirements(
            forecast_data=forecast_data,
            current_stock=current_stock or {}
        )
        
        return {
            "ingredient_requirements": requirements,
            "total_ingredients": len(requirements),
            "total_cost": sum(req['total_cost'] for req in requirements),
            "critical_items": [req for req in requirements if req['urgency'] == 'critical'],
            "high_priority_items": [req for req in requirements if req['urgency'] == 'high']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inventory calculation error: {str(e)}")

@router.get("/menu-items")
async def get_menu_items():
    """Get available menu items and their ingredient requirements"""
    return {
        "menu_items": inventory_manager.menu_items,
        "total_items": len(inventory_manager.menu_items)
    }

@router.get("/suppliers")
async def get_suppliers():
    """Get supplier information"""
    return {
        "suppliers": inventory_manager.suppliers,
        "total_suppliers": len(inventory_manager.suppliers)
    }

@router.put("/menu-items")
async def update_menu_items(
    menu_items: Dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update menu items configuration"""
    try:
        inventory_manager.update_menu_items(menu_items)
        return {"message": "Menu items updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update error: {str(e)}")

@router.put("/suppliers")
async def update_suppliers(
    suppliers: Dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update supplier configuration"""
    try:
        inventory_manager.update_suppliers(suppliers)
        return {"message": "Suppliers updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update error: {str(e)}")

@router.get("/stock-levels")
async def get_current_stock():
    """Get current stock levels (demo data)"""
    # In a real app, this would come from the database
    demo_stock = {
        "coffee_beans": 15.5,  # kg
        "milk": 8.0,  # liters
        "sugar": 12.0,  # kg
        "bread": 40,  # slices
        "cheese": 3.2,  # kg
        "ham": 1.8,  # kg
        "lettuce": 0.5,  # kg
        "tomato": 1.2,  # kg
        "mayo": 0.8,  # kg
        "flour": 18.0,  # kg
        "butter": 2.5,  # kg
        "yeast": 0.3,  # kg
        "egg": 24,  # units
        "cup": 150,  # units
        "lid": 150,  # units
        "wrapping_paper": 200  # units
    }
    
    return {
        "current_stock": demo_stock,
        "total_items": len(demo_stock),
        "last_updated": datetime.now().isoformat()
    }

@router.post("/update-stock")
async def update_stock_levels(
    stock_updates: Dict[str, float],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update stock levels"""
    try:
        # In a real app, this would update the database
        return {
            "message": "Stock levels updated successfully",
            "updated_items": len(stock_updates),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stock update error: {str(e)}")

# CRUD Operations
@router.post("/", response_model=InventoryItemResponse)
async def create_inventory_item(
    item: InventoryItemCreate,
    user: dict = Depends(lambda: {"uid": "test-user"})  # Placeholder for auth
):
    """Create a new inventory item - Optimized for speed"""
    start_time = time.time()
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
        
        # Prepare item data
        item_data = {
            **item.dict(),
            "userId": user["uid"],
            "lastUpdated": datetime.now()
        }
        
        # Single Firestore operation - just add the document
        firestore_start = time.time()
        doc_ref = db.collection("inventory").add(item_data)
        firestore_end = time.time()
        
        # Calculate timing
        firestore_duration = firestore_end - firestore_start
        total_duration = time.time() - start_time
        
        # Log performance
        log_performance("Firestore add inventory", firestore_duration, f"item: {item.name}")
        log_performance("Total create_inventory_item", total_duration, f"item: {item.name}")
        
        # Invalidate cache after creating new item
        invalidate_cache("inventory")
        
        # Return response immediately without extra get operation
        return {
            "id": doc_ref[1].id,
            **item_data
        }
        
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"[PERF] create_inventory_item failed after {total_time:.3f}s: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating inventory item: {str(e)}"
        )

@router.get("/", response_model=List[InventoryItemResponse])
@cached(ttl=60, key_prefix="inventory")  # Cache for 1 minute
async def get_inventory_items(
    user: dict = Depends(lambda: {"uid": "test-user"}),  # Placeholder for auth
    category: Optional[str] = None,
    low_stock: Optional[bool] = None
):
    """Get all inventory items for the current user - Cached for performance"""
    start_time = time.time()
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
        
        # Start timing Firestore query
        firestore_start = time.time()
        inventory_ref = db.collection("inventory")
        query = inventory_ref.where("userId", "==", user["uid"])
        
        if category:
            query = query.where("category", "==", category)
        
        docs = query.stream()
        items = []
        
        for doc in docs:
            item_data = doc.to_dict()
            item_data["id"] = doc.id
            items.append(item_data)
        
        firestore_end = time.time()
        log_performance("Firestore query", firestore_end - firestore_start, f"retrieved {len(items)} items")
        
        # Filter by low stock if requested
        if low_stock is not None:
            filter_start = time.time()
            if low_stock:
                items = [item for item in items if item["currentStock"] <= item["minStock"]]
            else:
                items = [item for item in items if item["currentStock"] > item["minStock"]]
            filter_end = time.time()
            log_performance("Low stock filtering", filter_end - filter_start, f"filtered to {len(items)} items")
        
        total_time = time.time() - start_time
        log_performance("Total get_inventory_items", total_time, f"returned {len(items)} items")
        
        return items
        
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"[PERF] get_inventory_items failed after {total_time:.3f}s: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching inventory items: {str(e)}"
        )

@router.get("/{item_id}", response_model=InventoryItemResponse)
async def get_inventory_item(
    item_id: str,
    user: dict = Depends(lambda: {"uid": "test-user"})  # Placeholder for auth
):
    """Get a specific inventory item"""
    start_time = time.time()
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
        
        firestore_start = time.time()
        doc_ref = db.collection("inventory").document(item_id)
        doc = doc_ref.get()
        firestore_end = time.time()
        log_performance("Firestore get document", firestore_end - firestore_start, f"item_id: {item_id}")
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Inventory item not found")
        
        item_data = doc.to_dict()
        if item_data["userId"] != user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        item_data["id"] = doc.id
        
        total_time = time.time() - start_time
        log_performance("Total get_inventory_item", total_time, f"item_id: {item_id}")
        
        return item_data
        
    except HTTPException:
        raise
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"[PERF] get_inventory_item failed after {total_time:.3f}s: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching inventory item: {str(e)}"
        )

@router.put("/{item_id}", response_model=InventoryItemResponse)
async def update_inventory_item(
    item_id: str,
    item_update: InventoryItemUpdate,
    user: dict = Depends(lambda: {"uid": "test-user"})  # Placeholder for auth
):
    """Update an inventory item"""
    start_time = time.time()
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
        
        # Get existing document
        firestore_start = time.time()
        doc_ref = db.collection("inventory").document(item_id)
        doc = doc_ref.get()
        firestore_end = time.time()
        log_performance("Firestore get for update", firestore_end - firestore_start, f"item_id: {item_id}")
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Inventory item not found")
        
        item_data = doc.to_dict()
        if item_data["userId"] != user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update only provided fields
        update_data = {k: v for k, v in item_update.dict().items() if v is not None}
        update_data["lastUpdated"] = datetime.now()
        
        # Perform update
        update_start = time.time()
        doc_ref.update(update_data)
        update_end = time.time()
        log_performance("Firestore update", update_end - update_start, f"item_id: {item_id}")
        
        # Get updated document
        get_updated_start = time.time()
        updated_doc = doc_ref.get()
        updated_data = updated_doc.to_dict()
        updated_data["id"] = updated_doc.id
        get_updated_end = time.time()
        log_performance("Firestore get updated", get_updated_end - get_updated_start, f"item_id: {item_id}")
        
        total_time = time.time() - start_time
        log_performance("Total update_inventory_item", total_time, f"item_id: {item_id}")
        
        return updated_data
        
    except HTTPException:
        raise
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"[PERF] update_inventory_item failed after {total_time:.3f}s: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating inventory item: {str(e)}"
        )

@router.delete("/{item_id}")
async def delete_inventory_item(
    item_id: str,
    user: dict = Depends(lambda: {"uid": "test-user"})  # Placeholder for auth
):
    """Delete an inventory item"""
    start_time = time.time()
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
        
        # Get existing document
        firestore_start = time.time()
        doc_ref = db.collection("inventory").document(item_id)
        doc = doc_ref.get()
        firestore_end = time.time()
        log_performance("Firestore get for delete", firestore_end - firestore_start, f"item_id: {item_id}")
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Inventory item not found")
        
        item_data = doc.to_dict()
        if item_data["userId"] != user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Perform delete
        delete_start = time.time()
        doc_ref.delete()
        delete_end = time.time()
        log_performance("Firestore delete", delete_end - delete_start, f"item_id: {item_id}")
        
        total_time = time.time() - start_time
        log_performance("Total delete_inventory_item", total_time, f"item_id: {item_id}")
        
        return {"message": "Inventory item deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"[PERF] delete_inventory_item failed after {total_time:.3f}s: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting inventory item: {str(e)}"
        )

@router.patch("/{item_id}/stock")
async def update_stock(
    item_id: str,
    stock_update: StockUpdate,
    user: dict = Depends(lambda: {"uid": "test-user"})  # Placeholder for auth
):
    """Update stock level for an inventory item"""
    start_time = time.time()
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
        
        # Get existing document
        firestore_start = time.time()
        doc_ref = db.collection("inventory").document(item_id)
        doc = doc_ref.get()
        firestore_end = time.time()
        log_performance("Firestore get for stock update", firestore_end - firestore_start, f"item_id: {item_id}")
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Inventory item not found")
        
        item_data = doc.to_dict()
        if item_data["userId"] != user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update stock
        update_data = {
            "currentStock": stock_update.newStock,
            "lastUpdated": datetime.now()
        }
        
        # Add to stock history if reason provided
        if stock_update.reason:
            history_start = time.time()
            history_ref = doc_ref.collection("stock_history")
            history_ref.add({
                "previousStock": item_data["currentStock"],
                "newStock": stock_update.newStock,
                "reason": stock_update.reason,
                "timestamp": datetime.now(),
                "userId": user["uid"]
            })
            history_end = time.time()
            log_performance("Firestore add history", history_end - history_start, f"item_id: {item_id}")
        
        # Update main document
        update_start = time.time()
        doc_ref.update(update_data)
        update_end = time.time()
        log_performance("Firestore stock update", update_end - update_start, f"item_id: {item_id}")
        
        total_time = time.time() - start_time
        log_performance("Total update_stock", total_time, f"item_id: {item_id}")
        
        return {
            "message": "Stock updated successfully",
            "previousStock": item_data["currentStock"],
            "newStock": stock_update.newStock,
            "itemId": item_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"[PERF] update_stock failed after {total_time:.3f}s: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating stock: {str(e)}"
        )

@router.get("/analytics/summary")
async def get_inventory_summary(
    user: dict = Depends(lambda: {"uid": "test-user"})  # Placeholder for auth
):
    """Get inventory analytics summary"""
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
            
        inventory_ref = db.collection("inventory")
        query = inventory_ref.where("userId", "==", user["uid"])
        docs = query.stream()
        
        items = []
        total_value = 0
        low_stock_count = 0
        out_of_stock_count = 0
        categories = {}
        
        for doc in docs:
            item_data = doc.to_dict()
            items.append(item_data)
            
            # Calculate total value
            item_value = item_data["currentStock"] * item_data["costPerUnit"]
            total_value += item_value
            
            # Count low stock items
            if item_data["currentStock"] <= item_data["minStock"]:
                low_stock_count += 1
            
            # Count out of stock items
            if item_data["currentStock"] <= 0:
                out_of_stock_count += 1
            
            # Count by category
            category = item_data["category"]
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
        
        return {
            "total_items": len(items),
            "total_value": round(total_value, 2),
            "low_stock_count": low_stock_count,
            "out_of_stock_count": out_of_stock_count,
            "categories": categories,
            "average_stock_level": round(sum(item["currentStock"] for item in items) / len(items), 2) if items else 0,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching inventory summary: {str(e)}"
        )

@router.get("/search/{query}")
async def search_inventory(
    query: str,
    user: dict = Depends(lambda: {"uid": "test-user"})  # Placeholder for auth
):
    """Search inventory items by name or category"""
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
            
        inventory_ref = db.collection("inventory")
        query_filter = inventory_ref.where("userId", "==", user["uid"])
        docs = query_filter.stream()
        
        items = []
        query_lower = query.lower()
        
        for doc in docs:
            item_data = doc.to_dict()
            
            # Search in name and category
            if (query_lower in item_data["name"].lower() or 
                query_lower in item_data["category"].lower()):
                item_data["id"] = doc.id
                items.append(item_data)
        
        return {
            "query": query,
            "results": items,
            "count": len(items)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching inventory: {str(e)}"
        ) 