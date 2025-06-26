from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Optional
from datetime import datetime
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