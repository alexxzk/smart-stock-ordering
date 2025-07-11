# -*- coding: utf-8 -*-
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import firebase_admin
from firebase_admin import auth
import os
from dotenv import load_dotenv
import time
import logging

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
from app.api import pos_integrations as pos_integrations_router
from app.api import users as users_router
from app.api import super_admin as super_admin_router
from app.api import sales_deduction as sales_deduction_router
from app.api import setup_wizard as setup_wizard_router
from app.api import supplier_api_integrations as supplier_api_router
from app.routes import integrations as integrations_router
from app.firebase_init import get_firestore_client
from app.api.cache import router as cache_router

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firebase and Firestore
get_firestore_client()

# Check if we're in development mode
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

app = FastAPI(
    title="Smart Stock Ordering API",
    description="AI-powered inventory management for cafes and restaurants",
    version="1.0.0"
)

# Add performance middleware
@app.middleware("http")
async def add_performance_logging(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    # Log slow requests (>1 second)
    if duration > 1.0:
        logger.warning(f"[PERF] Slow request: {request.method} {request.url.path} took {duration:.3f}s")
    else:
        logger.info(f"[PERF] Request: {request.method} {request.url.path} took {duration:.3f}s")
    
    return response

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:3000",
        "https://smart-stock-ordering.vercel.app",  # Vercel frontend
        os.getenv("FRONTEND_URL", ""),  # Allow custom frontend URL via env var
        "https://smart-stock-ordering-clean-22.onrender.com",  # Your frontend URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Gzip compression for better performance
app.add_middleware(GZipMiddleware, minimum_size=1000)

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
    pos_integrations_router.router, 
    prefix="/api/pos-integrations", 
    tags=["POS Integrations"],
    dependencies=[Depends(verify_token)]
)
app.include_router(
    users_router.router, 
    prefix="/api/users", 
    tags=["Users"],
    dependencies=[Depends(verify_token)]
)
app.include_router(
    super_admin_router.router, 
    prefix="/api/super-admin", 
    tags=["Super Admin"],
    dependencies=[Depends(verify_token)]
)
app.include_router(
    sales_deduction_router.router, 
    prefix="/api/sales-deduction", 
    tags=["Sales Auto-Deduction"],
    dependencies=[Depends(verify_token)]
)
app.include_router(
    setup_wizard_router.router, 
    prefix="/api/setup-wizard", 
    tags=["Setup Wizard"],
    dependencies=[Depends(verify_token)]
)
app.include_router(
    supplier_api_router.router, 
    prefix="/api/supplier-api-integrations", 
    tags=["Supplier API Integrations"],
    dependencies=[Depends(verify_token)]
)
app.include_router(
    integrations_router.router, 
    prefix="/api/integrations", 
    tags=["Integrations"],
    dependencies=[Depends(verify_token)]
)
app.include_router(
    cache_router, 
    prefix="/api/cache", 
    tags=["Cache Management"],
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
        db = get_firestore_client()
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

@app.get("/test-redis")
async def test_redis():
    """Test endpoint to verify Redis connection"""
    try:
        from app.cache_redis import redis_client
        if redis_client is None:
            return {"error": "Redis not initialized"}
        
        # Test Redis connection
        redis_client.set("test_key", "test_value", ex=60)
        value = redis_client.get("test_key")
        
        if value:
            return {
                "status": "success",
                "message": "Redis connection working!",
                "test_value": value.decode('utf-8')
            }
        else:
            return {"error": "Redis test failed"}
            
    except Exception as e:
        return {"error": f"Redis test failed: {str(e)}"}

@app.get("/api-info")
async def get_api_info():
    """Get API information and available endpoints"""
    return {
        "name": "Smart Stock Ordering API",
        "version": "1.0.0",
        "description": "AI-powered inventory management for cafes and restaurants",
        "endpoints": {
            "authentication": "/api/auth",
            "forecasting": "/api/forecasting",
            "inventory": "/api/inventory",
            "orders": "/api/orders",
            "ai_ordering": "/api/ordering",
            "excel_processor": "/api/excel-processor",
            "suppliers": "/api/suppliers",
            "supplier_integrations": "/api/supplier-integrations",
            "pos_integrations": "/api/pos-integrations",
            "users": "/api/users",
            "super_admin": "/api/super-admin",
            "sales_deduction": "/api/sales-deduction",
            "integrations": "/api/integrations",
            "cache": "/api/cache"
        },
        "docs": "/docs",
        "redoc": "/redoc",
        "dev_mode": DEV_MODE
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 