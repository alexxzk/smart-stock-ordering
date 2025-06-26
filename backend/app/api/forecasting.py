from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import pandas as pd
import json
from datetime import date, datetime
from typing import List, Dict
import io
import asyncio
from concurrent.futures import ThreadPoolExecutor
import os

from app.ml.forecasting import SalesForecaster
from app.models.sales import ForecastRequest, ForecastResult, SalesDataUpload
from app.firebase_init import get_firestore_client
from firebase_admin import auth

router = APIRouter()
security = HTTPBearer(auto_error=False)

# Check if we're in development mode
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

# Initialize forecaster
forecaster = SalesForecaster()

def process_batch(batch_data, user_id, business_id=None):
    """Process a batch of records in a separate thread"""
    try:
        db = get_firestore_client()
        if db is None:
            return {"success": False, "error": "Database not available"}
        
        batch = db.batch()
        collection_ref = db.collection('sales')
        
        for record in batch_data:
            doc_ref = collection_ref.document()
            record_to_save = {
                **record,
                "userId": user_id,
            }
            if business_id:
                record_to_save["businessId"] = business_id
            batch.set(doc_ref, record_to_save)
        
        batch.commit()
        return {"success": True, "count": len(batch_data)}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get user ID from token or use dev mode"""
    if DEV_MODE:
        return "dev-user-123"
    
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        decoded_token = auth.verify_id_token(credentials.credentials)
        return decoded_token['uid']
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid authentication token: {str(e)}")

@router.post("/upload-csv")
async def upload_sales_csv(
    file: UploadFile = File(...),
    user_id: str = Depends(get_user_id)
):
    """Upload CSV file with sales data and save to Firestore using optimized batch writes"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        # Read CSV file
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        
        # Optionally get businessId from token or request
        business_id = None

        # Convert to list of dictionaries and add userId
        sales_data = []
        for _, row in df.iterrows():
            # Extract date, item, quantity, and revenue with flexible column names
            date_col = next((col for col in df.columns if 'date' in col.lower()), 'date')
            item_col = next((col for col in df.columns if 'item' in col.lower() or 'product' in col.lower()), 'item')
            quantity_col = next((col for col in df.columns if 'quantity' in col.lower() or 'qty' in col.lower()), 'quantity')
            revenue_col = next((col for col in df.columns if 'revenue' in col.lower() or 'sales' in col.lower() or 'price' in col.lower()), 'revenue')
            
            record = {
                "date": str(row.get(date_col, datetime.now().date())),
                "item": str(row.get(item_col, 'Unknown Item')),
                "quantity": float(row.get(quantity_col, 0)) or 0,
                "revenue": float(row.get(revenue_col, 0)) or 0,
                "userId": user_id
            }
            
            # Only add records with valid data
            if record["quantity"] > 0 or record["revenue"] > 0:
                sales_data.append(record)

        if not sales_data:
            raise HTTPException(status_code=400, detail="No valid sales records found in CSV")

        # Use larger batch size for better performance (Firestore limit is 500)
        batch_size = 450  # Leave some buffer
        total_batches = (len(sales_data) + batch_size - 1) // batch_size
        
        # Process batches in parallel for maximum speed
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for i in range(0, len(sales_data), batch_size):
                batch = sales_data[i:i + batch_size]
                future = executor.submit(process_batch, batch, user_id, business_id)
                futures.append(future)
            
            # Wait for all batches to complete
            results = []
            for future in futures:
                result = future.result()
                results.append(result)
        
        # Check for errors
        failed_batches = [r for r in results if not r["success"]]
        if failed_batches:
            error_msg = f"Failed to process {len(failed_batches)} batches: {failed_batches[0]['error']}"
            raise HTTPException(status_code=500, detail=error_msg)
        
        # Calculate summary statistics
        total_sales = sum(record["revenue"] for record in sales_data)
        average_daily_sales = total_sales / len(sales_data) if sales_data else 0
        dates = [record["date"] for record in sales_data]
        date_range = {
            "start": min(dates) if dates else datetime.now().date().isoformat(),
            "end": max(dates) if dates else datetime.now().date().isoformat()
        }
        
        return SalesDataUpload(
            filename=file.filename,
            records_count=len(sales_data),
            date_range=date_range,
            total_sales=total_sales,
            average_daily_sales=average_daily_sales
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing CSV: {str(e)}")

@router.post("/forecast")
async def generate_forecast(
    request: ForecastRequest,
    user_id: str = Depends(get_user_id)
):
    """Generate sales forecast"""
    try:
        # For demo purposes, we'll use sample data
        # In a real app, you'd get this from the database
        sample_data = [
            {
                "date": "2024-01-01",
                "sales_amount": 1200.0,
                "orders_count": 45,
                "menu_items_sold": {"coffee": 20, "latte": 15, "sandwich": 10}
            },
            {
                "date": "2024-01-02", 
                "sales_amount": 1350.0,
                "orders_count": 52,
                "menu_items_sold": {"coffee": 25, "latte": 18, "sandwich": 9}
            },
            # Add more sample data...
        ]
        
        # Generate forecast
        forecast_result = forecaster.forecast(
            sales_data=sample_data,
            days=request.forecast_days,
            model_type=request.model_type,
            confidence_level=request.confidence_level
        )
        
        return ForecastResult(**forecast_result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast error: {str(e)}")

@router.get("/models")
async def get_available_models():
    """Get available forecasting models"""
    return {
        "models": [
            {
                "id": "prophet",
                "name": "Prophet",
                "description": "Facebook's time series forecasting model",
                "best_for": "Seasonal patterns, holidays, trend changes"
            },
            {
                "id": "random_forest",
                "name": "Random Forest",
                "description": "Ensemble learning method for regression",
                "best_for": "Non-linear relationships, feature importance"
            }
        ]
    } 