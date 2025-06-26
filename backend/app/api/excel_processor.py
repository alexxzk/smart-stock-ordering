from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import io
import tempfile
import os
from typing import List, Dict, Any

router = APIRouter()

@router.post("/process-excel")
async def process_excel_file(file: UploadFile = File(...)):
    """
    Process Excel file and return structured data
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(status_code=400, detail="File must be Excel (.xlsx, .xls) or CSV (.csv)")
        
        # Read file content
        content = await file.read()
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Read the file based on extension
            if file.filename.lower().endswith('.csv'):
                df = pd.read_csv(temp_file_path)
            else:
                # Try different Excel engines
                try:
                    df = pd.read_excel(temp_file_path, engine='openpyxl')
                except:
                    try:
                        df = pd.read_excel(temp_file_path, engine='xlrd')
                    except:
                        raise HTTPException(status_code=400, detail="Unable to read Excel file. Please convert to CSV format.")
            
            # Clean the data
            df = df.dropna(how='all').dropna(axis=1, how='all')
            
            # Convert to list format
            headers = df.columns.tolist()
            rows = df.values.tolist()
            
            # Create preview (first 5 rows)
            preview_rows = rows[:5] if len(rows) > 5 else rows
            
            result = {
                "headers": headers,
                "rows": rows,
                "preview": [headers] + preview_rows,
                "total_rows": len(rows),
                "total_columns": len(headers)
            }
            
            return JSONResponse(content=result)
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.post("/validate-sales-data")
async def validate_sales_data(data: Dict[str, Any]):
    """
    Validate that the data has required columns for sales analysis
    """
    try:
        headers = data.get("headers", [])
        
        # Define required columns (flexible matching)
        required_columns = ['date', 'item', 'quantity', 'revenue']
        missing_columns = []
        
        for required in required_columns:
            if not any(required in header.lower() for header in headers):
                missing_columns.append(required)
        
        if missing_columns:
            return {
                "valid": False,
                "missing_columns": missing_columns,
                "message": f"Missing required columns: {', '.join(missing_columns)}"
            }
        
        return {
            "valid": True,
            "message": "Data format is valid for sales analysis"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating data: {str(e)}") 