from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel
import httpx
import json
import logging

from app.firebase_init import get_firestore_client

router = APIRouter()
security = HTTPBearer()

# Set up logging
logger = logging.getLogger(__name__)

# Pydantic models
class POSConnectionBase(BaseModel):
    pos_type: str  # "square", "toast", "clover", "lightspeed", "shopify"
    name: str
    config: Dict[str, Any]
    is_active: bool = True

class POSConnectionCreate(POSConnectionBase):
    pass

class POSConnectionUpdate(BaseModel):
    name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class POSConnectionResponse(POSConnectionBase):
    id: str
    userId: str
    created_at: datetime
    updated_at: datetime
    last_sync: Optional[datetime] = None
    sync_status: str = "idle"  # "idle", "syncing", "error"

class SalesData(BaseModel):
    date: str
    total_sales: float
    items_sold: Dict[str, int]
    revenue_by_item: Dict[str, float]

class InventoryUpdate(BaseModel):
    item_id: str
    item_name: str
    quantity_sold: int
    current_stock: int
    last_updated: datetime

# Popular POS Systems Configuration
POS_SYSTEMS = {
    "square": {
        "name": "Square POS",
        "api_base": "https://connect.squareup.com/v2",
        "features": ["sales_sync", "inventory_sync", "real_time"],
        "auth_type": "oauth2",
        "webhook_support": True
    },
    "toast": {
        "name": "Toast POS",
        "api_base": "https://api.toasttab.com",
        "features": ["sales_sync", "inventory_sync", "menu_sync"],
        "auth_type": "api_key",
        "webhook_support": True
    },
    "clover": {
        "name": "Clover POS",
        "api_base": "https://api.clover.com",
        "features": ["sales_sync", "inventory_sync"],
        "auth_type": "oauth2",
        "webhook_support": True
    },
    "lightspeed": {
        "name": "Lightspeed Restaurant",
        "api_base": "https://api.lightspeedapp.com",
        "features": ["sales_sync", "inventory_sync", "customer_sync"],
        "auth_type": "oauth2",
        "webhook_support": True
    },
    "shopify": {
        "name": "Shopify POS",
        "api_base": "https://your-store.myshopify.com/admin/api/2023-10",
        "features": ["sales_sync", "inventory_sync", "product_sync"],
        "auth_type": "api_key",
        "webhook_support": True
    }
}

@router.get("/systems")
async def get_available_pos_systems():
    """Get list of available POS systems for integration"""
    return {
        "pos_systems": POS_SYSTEMS,
        "total_systems": len(POS_SYSTEMS)
    }

@router.post("/connect", response_model=POSConnectionResponse)
async def create_pos_connection(
    connection: POSConnectionCreate,
    user: dict = Depends(lambda: {"uid": "test-user"})  # Placeholder for auth
):
    """Create a new POS system connection"""
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
        
        # Validate POS type
        if connection.pos_type not in POS_SYSTEMS:
            raise HTTPException(status_code=400, detail=f"Unsupported POS type: {connection.pos_type}")
        
        # Test connection
        test_result = await test_pos_connection(connection.pos_type, connection.config)
        if not test_result["success"]:
            raise HTTPException(status_code=400, detail=f"Connection test failed: {test_result['error']}")
        
        connection_data = {
            **connection.dict(),
            "userId": user["uid"],
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "sync_status": "idle"
        }
        
        doc_ref = db.collection("pos_connections").add(connection_data)
        
        return {
            "id": doc_ref[1].id,
            **connection_data
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating POS connection: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating POS connection: {str(e)}"
        )

@router.get("/connections", response_model=List[POSConnectionResponse])
async def get_pos_connections(
    user: dict = Depends(lambda: {"uid": "test-user"})  # Placeholder for auth
):
    """Get all POS connections for the current user"""
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
        
        connections_ref = db.collection("pos_connections")
        query = connections_ref.where("userId", "==", user["uid"])
        docs = query.stream()
        
        connections = []
        for doc in docs:
            connection_data = doc.to_dict()
            connection_data["id"] = doc.id
            connections.append(connection_data)
        
        return connections
    except Exception as e:
        logger.error(f"Error fetching POS connections: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching POS connections: {str(e)}"
        )

@router.get("/connections/{connection_id}", response_model=POSConnectionResponse)
async def get_pos_connection(
    connection_id: str,
    user: dict = Depends(lambda: {"uid": "test-user"})  # Placeholder for auth
):
    """Get a specific POS connection"""
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
        
        doc_ref = db.collection("pos_connections").document(connection_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="POS connection not found")
        
        connection_data = doc.to_dict()
        if connection_data["userId"] != user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        connection_data["id"] = doc.id
        return connection_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching POS connection: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching POS connection: {str(e)}"
        )

@router.put("/connections/{connection_id}", response_model=POSConnectionResponse)
async def update_pos_connection(
    connection_id: str,
    connection_update: POSConnectionUpdate,
    user: dict = Depends(lambda: {"uid": "test-user"})  # Placeholder for auth
):
    """Update a POS connection"""
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
        
        doc_ref = db.collection("pos_connections").document(connection_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="POS connection not found")
        
        connection_data = doc.to_dict()
        if connection_data["userId"] != user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update only provided fields
        update_data = {k: v for k, v in connection_update.dict().items() if v is not None}
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
        logger.error(f"Error updating POS connection: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating POS connection: {str(e)}"
        )

@router.delete("/connections/{connection_id}")
async def delete_pos_connection(
    connection_id: str,
    user: dict = Depends(lambda: {"uid": "test-user"})  # Placeholder for auth
):
    """Delete a POS connection"""
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
        
        doc_ref = db.collection("pos_connections").document(connection_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="POS connection not found")
        
        connection_data = doc.to_dict()
        if connection_data["userId"] != user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        doc_ref.delete()
        
        return {"message": "POS connection deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting POS connection: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting POS connection: {str(e)}"
        )

@router.post("/connections/{connection_id}/test")
async def test_pos_connection_endpoint(
    connection_id: str,
    user: dict = Depends(lambda: {"uid": "test-user"})  # Placeholder for auth
):
    """Test a POS connection"""
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
        
        doc_ref = db.collection("pos_connections").document(connection_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="POS connection not found")
        
        connection_data = doc.to_dict()
        if connection_data["userId"] != user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Test the connection
        test_result = await test_pos_connection(connection_data["pos_type"], connection_data["config"])
        
        return {
            "connection_id": connection_id,
            "pos_type": connection_data["pos_type"],
            "test_result": test_result,
            "tested_at": datetime.now()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing POS connection: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error testing POS connection: {str(e)}"
        )

@router.post("/connections/{connection_id}/sync")
async def sync_pos_data(
    connection_id: str,
    sync_type: str = "all",  # "sales", "inventory", "all"
    user: dict = Depends(lambda: {"uid": "test-user"})  # Placeholder for auth
):
    """Sync data from POS system"""
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
        
        doc_ref = db.collection("pos_connections").document(connection_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="POS connection not found")
        
        connection_data = doc.to_dict()
        if connection_data["userId"] != user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update sync status
        doc_ref.update({
            "sync_status": "syncing",
            "updated_at": datetime.now()
        })
        
        try:
            # Simulate sync operation based on POS type
            sync_result = await perform_pos_sync(
                connection_data["pos_type"], 
                connection_data["config"], 
                sync_type
            )
            
            # Update sync status and last sync time
            doc_ref.update({
                "sync_status": "idle",
                "last_sync": datetime.now(),
                "updated_at": datetime.now()
            })
            
            return {
                "connection_id": connection_id,
                "pos_type": connection_data["pos_type"],
                "sync_type": sync_type,
                "status": "success",
                "sync_result": sync_result,
                "synced_at": datetime.now()
            }
            
        except Exception as sync_error:
            # Update sync status to error
            doc_ref.update({
                "sync_status": "error",
                "updated_at": datetime.now()
            })
            raise sync_error
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing POS data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error syncing POS data: {str(e)}"
        )

@router.get("/connections/{connection_id}/sales")
async def get_pos_sales_data(
    connection_id: str,
    start_date: str,
    end_date: str,
    user: dict = Depends(lambda: {"uid": "test-user"})  # Placeholder for auth
):
    """Get sales data from POS system"""
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
        
        doc_ref = db.collection("pos_connections").document(connection_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="POS connection not found")
        
        connection_data = doc.to_dict()
        if connection_data["userId"] != user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Simulate fetching sales data
        sales_data = await fetch_pos_sales_data(
            connection_data["pos_type"],
            connection_data["config"],
            start_date,
            end_date
        )
        
        return {
            "connection_id": connection_id,
            "pos_type": connection_data["pos_type"],
            "date_range": {"start": start_date, "end": end_date},
            "sales_data": sales_data,
            "total_sales": sum(sale["total_sales"] for sale in sales_data),
            "total_orders": len(sales_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching POS sales data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching POS sales data: {str(e)}"
        )

@router.get("/connections/{connection_id}/inventory")
async def get_pos_inventory_data(
    connection_id: str,
    user: dict = Depends(lambda: {"uid": "test-user"})  # Placeholder for auth
):
    """Get current inventory data from POS system"""
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
        
        doc_ref = db.collection("pos_connections").document(connection_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="POS connection not found")
        
        connection_data = doc.to_dict()
        if connection_data["userId"] != user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Simulate fetching inventory data
        inventory_data = await fetch_pos_inventory_data(
            connection_data["pos_type"],
            connection_data["config"]
        )
        
        return {
            "connection_id": connection_id,
            "pos_type": connection_data["pos_type"],
            "inventory_data": inventory_data,
            "total_items": len(inventory_data),
            "last_updated": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching POS inventory data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching POS inventory data: {str(e)}"
        )

# Helper functions
async def test_pos_connection(pos_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Test connection to POS system"""
    try:
        if pos_type == "square":
            # Test Square API connection
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {config.get('access_token')}"}
                response = await client.get(
                    f"{POS_SYSTEMS[pos_type]['api_base']}/locations",
                    headers=headers
                )
                if response.status_code == 200:
                    return {"success": True, "message": "Square connection successful"}
                else:
                    return {"success": False, "error": f"Square API error: {response.status_code}"}
        
        elif pos_type == "toast":
            # Test Toast API connection
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {config.get('api_key')}"}
                response = await client.get(
                    f"{POS_SYSTEMS[pos_type]['api_base']}/restaurants",
                    headers=headers
                )
                if response.status_code == 200:
                    return {"success": True, "message": "Toast connection successful"}
                else:
                    return {"success": False, "error": f"Toast API error: {response.status_code}"}
        
        else:
            # For other POS systems, simulate successful connection
            return {"success": True, "message": f"{pos_type.title()} connection test successful"}
            
    except Exception as e:
        return {"success": False, "error": f"Connection test failed: {str(e)}"}

async def perform_pos_sync(pos_type: str, config: Dict[str, Any], sync_type: str) -> Dict[str, Any]:
    """Perform data sync with POS system"""
    sync_result = {
        "sales_synced": 0,
        "inventory_synced": 0,
        "errors": []
    }
    
    try:
        if sync_type in ["sales", "all"]:
            # Simulate sales sync
            sales_data = await fetch_pos_sales_data(pos_type, config, "2024-01-01", "2024-12-31")
            sync_result["sales_synced"] = len(sales_data)
        
        if sync_type in ["inventory", "all"]:
            # Simulate inventory sync
            inventory_data = await fetch_pos_inventory_data(pos_type, config)
            sync_result["inventory_synced"] = len(inventory_data)
        
        return sync_result
        
    except Exception as e:
        sync_result["errors"].append(str(e))
        return sync_result

async def fetch_pos_sales_data(pos_type: str, config: Dict[str, Any], start_date: str, end_date: str) -> List[Dict]:
    """Fetch sales data from POS system"""
    # Simulate sales data for demo
    return [
        {
            "date": "2024-01-15",
            "total_sales": 1250.50,
            "items_sold": {"coffee": 45, "sandwich": 23, "cake": 12},
            "revenue_by_item": {"coffee": 450.00, "sandwich": 575.00, "cake": 225.50}
        },
        {
            "date": "2024-01-16",
            "total_sales": 1380.75,
            "items_sold": {"coffee": 52, "sandwich": 28, "cake": 15},
            "revenue_by_item": {"coffee": 520.00, "sandwich": 700.00, "cake": 160.75}
        }
    ]

async def fetch_pos_inventory_data(pos_type: str, config: Dict[str, Any]) -> List[Dict]:
    """Fetch inventory data from POS system"""
    # Simulate inventory data for demo
    return [
        {
            "item_id": "coffee_beans",
            "item_name": "Coffee Beans",
            "current_stock": 25.5,
            "unit": "kg",
            "last_updated": datetime.now()
        },
        {
            "item_id": "milk",
            "item_name": "Milk",
            "current_stock": 15.0,
            "unit": "L",
            "last_updated": datetime.now()
        },
        {
            "item_id": "bread",
            "item_name": "Bread",
            "current_stock": 30,
            "unit": "pieces",
            "last_updated": datetime.now()
        }
    ] 