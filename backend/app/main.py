# -*- coding: utf-8 -*-
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import auth
import os
from dotenv import load_dotenv

# Explicitly load config.env
load_dotenv("config.env")

from app.api import auth as auth_router
from app.api import forecasting as forecasting_router
from app.api import inventory as inventory_router
from app.api import orders as orders_router
from app.api import ordering as ordering_router
from app.api import excel_processor as excel_router
from app.api import suppliers as suppliers_router
from app.api import supplier_integrations as supplier_integrations_router
from app.api import users as users_router
from app.firebase_init import get_firestore_client

# Initialize Firebase and Firestore
db = get_firestore_client()

# Check if we're in development mode
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

app = FastAPI(
    title="Smart Stock Ordering API",
    description="AI-powered inventory management for cafes and restaurants",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify Firebase JWT token or bypass in dev mode"""
    if DEV_MODE:
        # Return a mock user in development mode
        return {
            "uid": "dev-user-123",
            "email": "dev@example.com",
            "name": "Development User"
        }
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Include routers
app.include_router(auth_router.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(
    forecasting_router.router, 
    prefix="/api/forecasting", 
    tags=["Forecasting"],
    dependencies=[Depends(verify_token)]
)
app.include_router(
    inventory_router.router, 
    prefix="/api/inventory", 
    tags=["Inventory"],
    dependencies=[Depends(verify_token)]
)
app.include_router(
    orders_router.router, 
    prefix="/api/orders", 
    tags=["Orders"],
    dependencies=[Depends(verify_token)]
)
app.include_router(
    ordering_router.router, 
    prefix="/api/ordering", 
    tags=["AI Ordering"],
    dependencies=[Depends(verify_token)]
)
app.include_router(
    excel_router.router, 
    prefix="/api/excel-processor", 
    tags=["Excel Processor"],
    dependencies=[Depends(verify_token)]
)
app.include_router(
    suppliers_router.router, 
    prefix="/api/suppliers", 
    tags=["Suppliers"],
    dependencies=[Depends(verify_token)]
)
app.include_router(
    supplier_integrations_router.router, 
    prefix="/api/supplier-integrations", 
    tags=["Supplier Integrations"],
    dependencies=[Depends(verify_token)]
)
app.include_router(
    users_router.router, 
    prefix="/api/users", 
    tags=["Users"],
    dependencies=[Depends(verify_token)]
)

@app.get("/")
async def root():
    return {
        "message": "Smart Stock Ordering API",
        "version": "1.0.0",
        "docs": "/docs",
        "dev_mode": DEV_MODE
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z", "dev_mode": DEV_MODE}

@app.get("/test-firestore")
async def test_firestore():
    """Test endpoint to verify Firestore connection"""
    try:
        if db is None:
            return {"error": "Firestore not initialized"}
        
        # Write a test document
        doc_ref = db.collection("test").document("ping")
        doc_ref.set({
            "message": "pong",
            "timestamp": "2024-01-01T00:00:00Z",
            "project_id": os.getenv("FIREBASE_PROJECT_ID", "unknown")
        })
        
        # Read it back
        doc = doc_ref.get()
        if doc.exists:
            return {
                "status": "success",
                "message": "Firestore connection working!",
                "data": doc.to_dict(),
                "project_id": os.getenv("FIREBASE_PROJECT_ID", "unknown")
            }
        else:
            return {"error": "Document not found after writing"}
            
    except Exception as e:
        return {"error": f"Firestore test failed: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 