from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Optional
from datetime import date, datetime
from pydantic import BaseModel
import time
import logging

from app.firebase_init import get_firestore_client
from app.cache_redis import cached, invalidate_cache

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Performance monitoring
def log_performance(operation: str, duration: float, details: str = ""):
    """Log performance metrics"""
    logger.info(f"[PERF] {operation} took {duration:.3f}s {details}")

@router.post("/", response_model=SupplierResponse)
async def create_supplier(
    supplier: SupplierCreate,
    user: dict = Depends(lambda: {"uid": "test-user"})  # Placeholder for auth
):
    """Create a new supplier - Optimized for speed"""
    start_time = time.time()
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
        
        # Prepare supplier data
        supplier_data = {
            **supplier.dict(),
            "userId": user["uid"],
            "createdAt": datetime.now(),
            "lastUpdated": datetime.now()
        }
        
        # Single Firestore operation - just add the document
        firestore_start = time.time()
        doc_ref = db.collection("suppliers").add(supplier_data)
        firestore_end = time.time()
        
        # Calculate timing
        firestore_duration = firestore_end - firestore_start
        total_duration = time.time() - start_time
        
        # Log performance
        log_performance("Firestore add supplier", firestore_duration, f"supplier: {supplier.name}")
        log_performance("Total create_supplier", total_duration, f"supplier: {supplier.name}")
        
        # Invalidate cache after creating new supplier
        invalidate_cache("suppliers")
        
        # Return response immediately without extra get operation
        return {
            "id": doc_ref[1].id,
            **supplier_data
        }
        
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"[PERF] create_supplier failed after {total_time:.3f}s: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating supplier: {str(e)}"
        )

@router.get("/", response_model=List[SupplierResponse])
@cached(ttl=120, key_prefix="suppliers")  # Cache for 2 minutes
async def get_suppliers(
    user: dict = Depends(lambda: {"uid": "test-user"}),  # Placeholder for auth
    category: Optional[str] = None
):
    """Get all suppliers for the current user - Cached for performance"""
    start_time = time.time()
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
        
        # Start timing Firestore query
        firestore_start = time.time()
        suppliers_ref = db.collection("suppliers")
        query = suppliers_ref.where("userId", "==", user["uid"])
        
        if category:
            query = query.where("category", "==", category)
        
        docs = query.stream()
        suppliers = []
        
        for doc in docs:
            supplier_data = doc.to_dict()
            supplier_data["id"] = doc.id
            suppliers.append(supplier_data)
        
        firestore_end = time.time()
        log_performance("Firestore query suppliers", firestore_end - firestore_start, f"retrieved {len(suppliers)} suppliers")
        
        total_time = time.time() - start_time
        log_performance("Total get_suppliers", total_time, f"returned {len(suppliers)} suppliers")
        
        return suppliers
        
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"[PERF] get_suppliers failed after {total_time:.3f}s: {str(e)}")
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
    start_time = time.time()
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
            
        firestore_start = time.time()
        doc_ref = db.collection("suppliers").document(supplier_id)
        doc = doc_ref.get()
        firestore_end = time.time()
        log_performance("Firestore get supplier", firestore_end - firestore_start, f"supplier_id: {supplier_id}")
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Supplier not found")
        
        supplier_data = doc.to_dict()
        if supplier_data["userId"] != user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        supplier_data["id"] = doc.id
        
        total_time = time.time() - start_time
        log_performance("Total get_supplier", total_time, f"supplier_id: {supplier_id}")
        
        return supplier_data
        
    except HTTPException:
        raise
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"[PERF] get_supplier failed after {total_time:.3f}s: {str(e)}")
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
    start_time = time.time()
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
            
        # Get existing document
        firestore_start = time.time()
        doc_ref = db.collection("suppliers").document(supplier_id)
        doc = doc_ref.get()
        firestore_end = time.time()
        log_performance("Firestore get for update", firestore_end - firestore_start, f"supplier_id: {supplier_id}")
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Supplier not found")
        
        supplier_data = doc.to_dict()
        if supplier_data["userId"] != user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update only provided fields
        update_data = {k: v for k, v in supplier_update.dict().items() if v is not None}
        update_data["updated_at"] = datetime.now()
        
        # Perform update
        update_start = time.time()
        doc_ref.update(update_data)
        update_end = time.time()
        log_performance("Firestore update supplier", update_end - update_start, f"supplier_id: {supplier_id}")
        
        # Get updated document
        get_updated_start = time.time()
        updated_doc = doc_ref.get()
        updated_data = updated_doc.to_dict()
        updated_data["id"] = updated_doc.id
        get_updated_end = time.time()
        log_performance("Firestore get updated supplier", get_updated_end - get_updated_start, f"supplier_id: {supplier_id}")
        
        total_time = time.time() - start_time
        log_performance("Total update_supplier", total_time, f"supplier_id: {supplier_id}")
        
        return updated_data
        
    except HTTPException:
        raise
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"[PERF] update_supplier failed after {total_time:.3f}s: {str(e)}")
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
    start_time = time.time()
    try:
        db = get_firestore_client()
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
            
        # Get existing document
        firestore_start = time.time()
        doc_ref = db.collection("suppliers").document(supplier_id)
        doc = doc_ref.get()
        firestore_end = time.time()
        log_performance("Firestore get for delete", firestore_end - firestore_start, f"supplier_id: {supplier_id}")
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Supplier not found")
        
        supplier_data = doc.to_dict()
        if supplier_data["userId"] != user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Perform delete
        delete_start = time.time()
        doc_ref.delete()
        delete_end = time.time()
        log_performance("Firestore delete supplier", delete_end - delete_start, f"supplier_id: {supplier_id}")
        
        total_time = time.time() - start_time
        log_performance("Total delete_supplier", total_time, f"supplier_id: {supplier_id}")
        
        return {"message": "Supplier deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"[PERF] delete_supplier failed after {total_time:.3f}s: {str(e)}")
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