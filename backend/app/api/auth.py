from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth
from typing import Dict, Optional

router = APIRouter()
security = HTTPBearer()

@router.post("/verify")
async def verify_token(credentials: HTTPAuthorizationCredentials):
    """Verify Firebase JWT token"""
    try:
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        return {
            "valid": True,
            "uid": decoded_token["uid"],
            "email": decoded_token.get("email"),
            "name": decoded_token.get("name")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@router.get("/user/{uid}")
async def get_user_info(uid: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get user information from Firebase"""
    try:
        # Verify the token first
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        
        # Get user info
        user = auth.get_user(uid)
        return {
            "uid": user.uid,
            "email": user.email,
            "display_name": user.display_name,
            "photo_url": user.photo_url,
            "email_verified": user.email_verified,
            "disabled": user.disabled
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        ) 