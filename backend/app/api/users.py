from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth, firestore
import json
from datetime import datetime
from typing import Dict, Any

router = APIRouter(prefix="/api/users", tags=["users"])
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

@router.post("/export-data")
async def export_user_data(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Export all user data for GDPR compliance
    """
    try:
        db = firestore.client()
        user_id = current_user['uid']
        
        # Collect all user data
        user_data = {
            "export_date": datetime.now().isoformat(),
            "user_id": user_id,
            "user_profile": {},
            "business_data": {},
            "sales_data": [],
            "inventory_data": [],
            "orders_data": [],
            "suppliers_data": [],
            "ml_models": [],
            "privacy_consent": {},
            "data_deletion_requests": []
        }
        
        # Get user profile
        try:
            user_doc = db.collection('users').document(user_id).get()
            if user_doc.exists:
                user_data["user_profile"] = user_doc.to_dict()
        except Exception as e:
            print(f"Error fetching user profile: {e}")
        
        # Get business data
        try:
            business_docs = db.collection('businesses').where('ownerIds', 'array_contains', user_id).stream()
            for doc in business_docs:
                user_data["business_data"][doc.id] = doc.to_dict()
        except Exception as e:
            print(f"Error fetching business data: {e}")
        
        # Get sales data
        try:
            for business_id in user_data["business_data"].keys():
                sales_docs = db.collection('sales').where('businessId', '==', business_id).stream()
                for doc in sales_docs:
                    user_data["sales_data"].append(doc.to_dict())
        except Exception as e:
            print(f"Error fetching sales data: {e}")
        
        # Get inventory data
        try:
            for business_id in user_data["business_data"].keys():
                inventory_docs = db.collection('inventory').where('businessId', '==', business_id).stream()
                for doc in inventory_docs:
                    user_data["inventory_data"].append(doc.to_dict())
        except Exception as e:
            print(f"Error fetching inventory data: {e}")
        
        # Get orders data
        try:
            for business_id in user_data["business_data"].keys():
                orders_docs = db.collection('orders').where('businessId', '==', business_id).stream()
                for doc in orders_docs:
                    user_data["orders_data"].append(doc.to_dict())
        except Exception as e:
            print(f"Error fetching orders data: {e}")
        
        # Get suppliers data
        try:
            for business_id in user_data["business_data"].keys():
                suppliers_docs = db.collection('suppliers').where('businessId', '==', business_id).stream()
                for doc in suppliers_docs:
                    user_data["suppliers_data"].append(doc.to_dict())
        except Exception as e:
            print(f"Error fetching suppliers data: {e}")
        
        # Get ML models
        try:
            for business_id in user_data["business_data"].keys():
                models_docs = db.collection('ml_models').where('businessId', '==', business_id).stream()
                for doc in models_docs:
                    user_data["ml_models"].append(doc.to_dict())
        except Exception as e:
            print(f"Error fetching ML models: {e}")
        
        # Get privacy consent
        try:
            consent_doc = db.collection('privacy_consent').document(user_id).get()
            if consent_doc.exists:
                user_data["privacy_consent"] = consent_doc.to_dict()
        except Exception as e:
            print(f"Error fetching privacy consent: {e}")
        
        # Get data deletion requests
        try:
            deletion_doc = db.collection('data_deletion_requests').document(user_id).get()
            if deletion_doc.exists:
                user_data["data_deletion_requests"] = [deletion_doc.to_dict()]
        except Exception as e:
            print(f"Error fetching deletion requests: {e}")
        
        # Convert to JSON
        json_data = json.dumps(user_data, indent=2, default=str)
        
        # Return as downloadable file
        return Response(
            content=json_data,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=user-data-{user_id}-{datetime.now().strftime('%Y%m%d')}.json"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting user data: {str(e)}")

@router.post("/request-data-deletion")
async def request_data_deletion(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Request data deletion for GDPR compliance
    """
    try:
        db = firestore.client()
        user_id = current_user['uid']
        
        # Create deletion request
        deletion_request = {
            "userId": user_id,
            "requestDate": datetime.now(),
            "status": "pending",
            "reason": "user_request",
            "dataTypes": ["profile", "sales", "inventory", "orders", "analytics"],
            "processedDate": None,
            "notes": ""
        }
        
        db.collection('data_deletion_requests').document(user_id).set(deletion_request)
        
        return {"message": "Data deletion request submitted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error requesting data deletion: {str(e)}")

@router.get("/privacy-settings")
async def get_privacy_settings(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get user privacy settings
    """
    try:
        db = firestore.client()
        user_id = current_user['uid']
        
        consent_doc = db.collection('privacy_consent').document(user_id).get()
        if consent_doc.exists:
            return consent_doc.to_dict()
        else:
            return {"message": "No privacy settings found"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching privacy settings: {str(e)}") 