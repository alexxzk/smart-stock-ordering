from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.firebase_init import get_firestore_client

router = APIRouter()
security = HTTPBearer()

# Pydantic models
class IntegrationBase(BaseModel):
    supplier_id: str
    integration_type: str  # "email", "api", "webhook"
    config: Dict
    is_active: bool = True

class IntegrationCreate(IntegrationBase):
    pass

class IntegrationUpdate(BaseModel):
    integration_type: Optional[str] = None
    config: Optional[Dict] = None
    is_active: Optional[bool] = None

class IntegrationResponse(IntegrationBase):
    id: str
    userId: str
    created_at: datetime
    updated_at: datetime
    last_sync: Optional[datetime] = None

@router.post("/", response_model=IntegrationResponse)
async def create_integration(
    integration: IntegrationCreate,
    user: dict = Depends(lambda: {"uid": "test-user"})  # Placeholder for auth
):
    """Create a new supplier integration"""
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
            
        integration_data = {
            **integration.dict(),
            "userId": user["uid"],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        doc_ref = db.collection("supplier_integrations").add(integration_data)
        
        return {
            "id": doc_ref[1].id,
            **integration_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating integration: {str(e)}"
        )

@router.get("/", response_model=List[IntegrationResponse])
async def get_integrations(
    user: dict = Depends(lambda: {"uid": "test-user"}),  # Placeholder for auth
    supplier_id: Optional[str] = None,
    integration_type: Optional[str] = None
):
    """Get all supplier integrations for the current user"""
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
            
        integrations_ref = db.collection("supplier_integrations")
        query = integrations_ref.where("userId", "==", user["uid"])
        
        if supplier_id:
            query = query.where("supplier_id", "==", supplier_id)
        
        if integration_type:
            query = query.where("integration_type", "==", integration_type)
        
        docs = query.stream()
        integrations = []
        
        for doc in docs:
            integration_data = doc.to_dict()
            integration_data["id"] = doc.id
            integrations.append(integration_data)
        
        return integrations
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching integrations: {str(e)}"
        )

@router.get("/{integration_id}", response_model=IntegrationResponse)
async def get_integration(
    integration_id: str,
    user: dict = Depends(lambda: {"uid": "test-user"})  # Placeholder for auth
):
    """Get a specific supplier integration"""
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
            
        doc_ref = db.collection("supplier_integrations").document(integration_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        integration_data = doc.to_dict()
        if integration_data["userId"] != user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        integration_data["id"] = doc.id
        return integration_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching integration: {str(e)}"
        )

@router.put("/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    integration_id: str,
    integration_update: IntegrationUpdate,
    user: dict = Depends(lambda: {"uid": "test-user"})  # Placeholder for auth
):
    """Update a supplier integration"""
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
            
        doc_ref = db.collection("supplier_integrations").document(integration_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        integration_data = doc.to_dict()
        if integration_data["userId"] != user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update only provided fields
        update_data = {k: v for k, v in integration_update.dict().items() if v is not None}
        update_data["updated_at"] = datetime.now()
        
        doc_ref.update(update_data)
        
        # Get updated document
        updated_doc = doc_ref.get()
        updated_data = updated_doc.to_dict()
        updated_data["id"] = updated_doc.id
        
        return updated_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating integration: {str(e)}"
        )

@router.delete("/{integration_id}")
async def delete_integration(
    integration_id: str,
    user: dict = Depends(lambda: {"uid": "test-user"})  # Placeholder for auth
):
    """Delete a supplier integration"""
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
            
        doc_ref = db.collection("supplier_integrations").document(integration_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        integration_data = doc.to_dict()
        if integration_data["userId"] != user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        doc_ref.delete()
        
        return {"message": "Integration deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting integration: {str(e)}"
        )

@router.post("/{integration_id}/test")
async def test_integration(
    integration_id: str,
    user: dict = Depends(lambda: {"uid": "test-user"})  # Placeholder for auth
):
    """Test a supplier integration"""
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
            
        doc_ref = db.collection("supplier_integrations").document(integration_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        integration_data = doc.to_dict()
        if integration_data["userId"] != user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Simulate integration test
        test_result = {
            "integration_id": integration_id,
            "status": "success",
            "message": "Integration test completed successfully",
            "tested_at": datetime.now(),
            "integration_type": integration_data.get("integration_type", "unknown")
        }
        
        return test_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error testing integration: {str(e)}"
        )

@router.post("/{integration_id}/sync")
async def sync_integration(
    integration_id: str,
    user: dict = Depends(lambda: {"uid": "test-user"})  # Placeholder for auth
):
    """Sync data with supplier integration"""
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
            
        doc_ref = db.collection("supplier_integrations").document(integration_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        integration_data = doc.to_dict()
        if integration_data["userId"] != user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Simulate sync operation
        sync_result = {
            "integration_id": integration_id,
            "status": "success",
            "message": "Data synchronized successfully",
            "synced_at": datetime.now(),
            "records_processed": 0,
            "integration_type": integration_data.get("integration_type", "unknown")
        }
        
        # Update last sync time
        doc_ref.update({"last_sync": datetime.now()})
        
        return sync_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error syncing integration: {str(e)}"
        )

@router.get("/analytics/summary")
async def get_integrations_summary(
    user: dict = Depends(lambda: {"uid": "test-user"})  # Placeholder for auth
):
    """Get summary analytics for integrations"""
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
            
        integrations_ref = db.collection("supplier_integrations")
        query = integrations_ref.where("userId", "==", user["uid"])
        docs = query.stream()
        
        total_integrations = 0
        active_integrations = 0
        integration_types = {}
        
        for doc in docs:
            total_integrations += 1
            integration_data = doc.to_dict()
            
            if integration_data.get("is_active", False):
                active_integrations += 1
            
            integration_type = integration_data.get("integration_type", "unknown")
            integration_types[integration_type] = integration_types.get(integration_type, 0) + 1
        
        summary = {
            "total_integrations": total_integrations,
            "active_integrations": active_integrations,
            "inactive_integrations": total_integrations - active_integrations,
            "integration_types": integration_types,
            "last_updated": datetime.now()
        }
        
        return summary
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching integration summary: {str(e)}"
        )

@router.get("/suppliers")
async def get_available_suppliers():
    """Get list of available suppliers for integration"""
    suppliers = {
        "sysco": {
            "id": "sysco",
            "name": "Sysco Corporation",
            "description": "Leading foodservice distribution company",
            "integration_type": "api",
            "api_url": "https://api.sysco.com",
            "website_url": "https://www.sysco.com",
            "features": ["real_time_pricing", "automated_ordering", "inventory_sync", "delivery_tracking"],
            "categories": ["food", "beverages", "supplies"],
            "delivery_areas": ["nationwide"],
            "minimum_order": 500.0,
            "delivery_lead_time": 2
        },
        "us_foods": {
            "id": "us_foods",
            "name": "US Foods",
            "description": "Premier foodservice distributor",
            "integration_type": "api",
            "api_url": "https://api.usfoods.com",
            "website_url": "https://www.usfoods.com",
            "features": ["real_time_pricing", "automated_ordering", "inventory_sync"],
            "categories": ["food", "beverages", "equipment"],
            "delivery_areas": ["nationwide"],
            "minimum_order": 300.0,
            "delivery_lead_time": 1
        },
        "gordon_food_service": {
            "id": "gordon_food_service",
            "name": "Gordon Food Service",
            "description": "Family-owned foodservice distributor",
            "integration_type": "web_scraping",
            "website_url": "https://www.gfs.com",
            "features": ["pricing_updates", "order_placement", "product_catalog"],
            "categories": ["food", "beverages", "supplies"],
            "delivery_areas": ["midwest", "east_coast"],
            "minimum_order": 200.0,
            "delivery_lead_time": 2
        },
        "local_produce": {
            "id": "local_produce",
            "name": "Local Produce Supplier",
            "description": "Fresh local produce and organic products",
            "integration_type": "email",
            "email": "orders@localproduce.com",
            "features": ["fresh_produce", "organic_options", "local_delivery"],
            "categories": ["produce", "organic"],
            "delivery_areas": ["local"],
            "minimum_order": 50.0,
            "delivery_lead_time": 1
        },
        "coffee_supplier": {
            "id": "coffee_supplier",
            "name": "Premium Coffee Roasters",
            "description": "Specialty coffee beans and equipment",
            "integration_type": "api",
            "api_url": "https://api.coffeesupplier.com",
            "website_url": "https://www.coffeesupplier.com",
            "features": ["coffee_beans", "equipment", "training"],
            "categories": ["coffee", "equipment"],
            "delivery_areas": ["nationwide"],
            "minimum_order": 100.0,
            "delivery_lead_time": 3
        },
        "dairy_supplier": {
            "id": "dairy_supplier",
            "name": "Fresh Dairy Co.",
            "description": "Fresh dairy products and alternatives",
            "integration_type": "manual",
            "phone": "555-0123",
            "features": ["fresh_dairy", "plant_based", "daily_delivery"],
            "categories": ["dairy", "alternatives"],
            "delivery_areas": ["local"],
            "minimum_order": 75.0,
            "delivery_lead_time": 1
        }
    }
    
    return {
        "suppliers": suppliers,
        "total_suppliers": len(suppliers),
        "integration_types": {
            "api": len([s for s in suppliers.values() if s["integration_type"] == "api"]),
            "web_scraping": len([s for s in suppliers.values() if s["integration_type"] == "web_scraping"]),
            "email": len([s for s in suppliers.values() if s["integration_type"] == "email"]),
            "manual": len([s for s in suppliers.values() if s["integration_type"] == "manual"])
        }
    }

@router.post("/pricing")
async def get_supplier_pricing(
    request: dict,
    user: dict = Depends(lambda: {"uid": "test-user"})  # Placeholder for auth
):
    """Get pricing for items from a specific supplier"""
    try:
        supplier_id = request.get("supplier_id")
        items = request.get("items", [])
        
        if not supplier_id or not items:
            raise HTTPException(status_code=400, detail="Supplier ID and items are required")
        
        # Simulate pricing data based on supplier
        pricing_data = []
        
        for item in items:
            # Generate mock pricing based on supplier and item
            base_price = 10.0 + (hash(item) % 50)  # Simple hash for demo
            supplier_multiplier = {
                "sysco": 1.0,
                "us_foods": 1.1,
                "gordon_food_service": 0.9,
                "local_produce": 1.2,
                "coffee_supplier": 1.3,
                "dairy_supplier": 1.0
            }.get(supplier_id, 1.0)
            
            price = base_price * supplier_multiplier
            
            pricing_data.append({
                "itemId": f"{supplier_id}_{item.lower().replace(' ', '_')}",
                "itemName": item,
                "price": round(price, 2),
                "currency": "USD",
                "unit": "kg" if "coffee" in item.lower() else "piece",
                "lastUpdated": datetime.now().isoformat(),
                "supplierId": supplier_id,
                "availability": "in_stock",
                "minimumOrder": 1
            })
        
        return {
            "supplier_id": supplier_id,
            "pricing": pricing_data,
            "total_items": len(pricing_data),
            "currency": "USD"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching pricing: {str(e)}"
        )

@router.post("/order")
async def place_supplier_order(
    request: dict,
    user: dict = Depends(lambda: {"uid": "test-user"})  # Placeholder for auth
):
    """Place an order with a supplier"""
    try:
        supplier_id = request.get("supplier_id")
        items = request.get("items", [])
        delivery_address = request.get("deliveryAddress")
        delivery_date = request.get("deliveryDate")
        notes = request.get("notes", "")
        
        if not supplier_id or not items or not delivery_address:
            raise HTTPException(status_code=400, detail="Supplier ID, items, and delivery address are required")
        
        # Calculate order total
        total_amount = sum(item.get("price", 0) * item.get("quantity", 0) for item in items)
        
        # Generate order ID
        order_id = f"order_{supplier_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Simulate order processing
        order_status = "confirmed"
        estimated_delivery = delivery_date or (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
        
        order_data = {
            "orderId": order_id,
            "supplierId": supplier_id,
            "items": items,
            "totalAmount": total_amount,
            "deliveryAddress": delivery_address,
            "deliveryDate": delivery_date,
            "estimatedDelivery": estimated_delivery,
            "notes": notes,
            "status": order_status,
            "createdAt": datetime.now().isoformat(),
            "currency": "USD"
        }
        
        # In a real implementation, this would be saved to the database
        # and sent to the supplier's system
        
        return {
            "success": True,
            "orderId": order_id,
            "message": f"Order placed successfully with {supplier_id}",
            "order": order_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error placing order: {str(e)}"
        ) 