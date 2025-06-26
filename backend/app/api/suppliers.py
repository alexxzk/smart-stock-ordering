from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel

from app.firebase_init import get_firestore_client

router = APIRouter()
security = HTTPBearer()

# Pydantic models
class SupplierBase(BaseModel):
    name: str
    contact_person: str
    email: str
    phone: str
    address: str
    payment_terms: str
    delivery_lead_time: int  # days
    minimum_order: float
    categories: List[str]

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    payment_terms: Optional[str] = None
    delivery_lead_time: Optional[int] = None
    minimum_order: Optional[float] = None
    categories: Optional[List[str]] = None

class SupplierResponse(SupplierBase):
    id: str
    userId: str
    created_at: datetime
    updated_at: datetime

@router.post("/", response_model=SupplierResponse)
async def create_supplier(
    supplier: SupplierCreate,
    user: dict = Depends(lambda: {"uid": "test-user"})  # Placeholder for auth
):
    """Create a new supplier"""
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
            
        supplier_data = {
            **supplier.dict(),
            "userId": user["uid"],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        doc_ref = db.collection("suppliers").add(supplier_data)
        
        return {
            "id": doc_ref[1].id,
            **supplier_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating supplier: {str(e)}"
        )

@router.get("/", response_model=List[SupplierResponse])
async def get_suppliers(
    user: dict = Depends(lambda: {"uid": "test-user"}),  # Placeholder for auth
    category: Optional[str] = None
):
    """Get all suppliers for the current user"""
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
            
        suppliers_ref = db.collection("suppliers")
        query = suppliers_ref.where("userId", "==", user["uid"])
        
        if category:
            query = query.where("categories", "array_contains", category)
        
        docs = query.stream()
        suppliers = []
        
        for doc in docs:
            supplier_data = doc.to_dict()
            supplier_data["id"] = doc.id
            suppliers.append(supplier_data)
        
        return suppliers
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching suppliers: {str(e)}"
        )

@router.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: str,
    user: dict = Depends(lambda: {"uid": "test-user"})  # Placeholder for auth
):
    """Get a specific supplier"""
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
            
        doc_ref = db.collection("suppliers").document(supplier_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Supplier not found")
        
        supplier_data = doc.to_dict()
        if supplier_data["userId"] != user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        supplier_data["id"] = doc.id
        return supplier_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching supplier: {str(e)}"
        )

@router.put("/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: str,
    supplier_update: SupplierUpdate,
    user: dict = Depends(lambda: {"uid": "test-user"})  # Placeholder for auth
):
    """Update a supplier"""
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
            
        doc_ref = db.collection("suppliers").document(supplier_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Supplier not found")
        
        supplier_data = doc.to_dict()
        if supplier_data["userId"] != user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update only provided fields
        update_data = {k: v for k, v in supplier_update.dict().items() if v is not None}
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
            detail=f"Error updating supplier: {str(e)}"
        )

@router.delete("/{supplier_id}")
async def delete_supplier(
    supplier_id: str,
    user: dict = Depends(lambda: {"uid": "test-user"})  # Placeholder for auth
):
    """Delete a supplier"""
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
            
        doc_ref = db.collection("suppliers").document(supplier_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Supplier not found")
        
        supplier_data = doc.to_dict()
        if supplier_data["userId"] != user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        doc_ref.delete()
        
        return {"message": "Supplier deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting supplier: {str(e)}"
        )

@router.get("/analytics/summary")
async def get_suppliers_summary(
    user: dict = Depends(lambda: {"uid": "test-user"})  # Placeholder for auth
):
    """Get suppliers analytics summary"""
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
            
        suppliers_ref = db.collection("suppliers")
        query = suppliers_ref.where("userId", "==", user["uid"])
        docs = query.stream()
        
        suppliers = []
        categories = {}
        total_lead_time = 0
        
        for doc in docs:
            supplier_data = doc.to_dict()
            suppliers.append(supplier_data)
            
            # Count by category
            for category in supplier_data["categories"]:
                if category not in categories:
                    categories[category] = 0
                categories[category] += 1
            
            total_lead_time += supplier_data["delivery_lead_time"]
        
        return {
            "total_suppliers": len(suppliers),
            "categories": categories,
            "average_lead_time": round(total_lead_time / len(suppliers), 1) if suppliers else 0,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching suppliers summary: {str(e)}"
        ) 