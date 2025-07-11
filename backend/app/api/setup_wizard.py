from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Optional
import logging

from app.models.setup_wizard import (
    SetupWizardSession, SetupStep, RestaurantProfile, MenuItemUpload,
    IngredientUpload, SupplierUpload, InitialStockUpload, SetupProgress,
    SetupValidation, SetupCompletion, CSVUploadRequest, CSVUploadResponse
)
from app.services.setup_wizard import SetupWizardService
from app.firebase_init import get_firestore_client

router = APIRouter(prefix="/api/setup-wizard", tags=["Setup Wizard"])
security = HTTPBearer()

# Set up logging
logger = logging.getLogger(__name__)

# Initialize setup wizard service
setup_wizard_service = SetupWizardService()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify Firebase JWT token"""
    try:
        from firebase_admin import auth
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication token")

@router.post("/create-session")
async def create_setup_session(
    current_user: Dict = Depends(get_current_user)
):
    """Create a new setup wizard session"""
    try:
        session = await setup_wizard_service.create_session(current_user.get('uid'))
        
        return {
            "message": "Setup session created successfully",
            "session_id": session.session_id,
            "current_step": session.current_step,
            "created_at": session.created_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating setup session: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating setup session: {str(e)}")

@router.get("/session/{session_id}")
async def get_setup_session(
    session_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get setup wizard session"""
    try:
        session = await setup_wizard_service.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "session_id": session.session_id,
            "current_step": session.current_step,
            "completed_steps": session.completed_steps,
            "is_completed": session.is_completed,
            "restaurant_id": session.restaurant_id,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting setup session: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting setup session: {str(e)}")

@router.get("/progress/{session_id}")
async def get_setup_progress(
    session_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get setup progress"""
    try:
        progress = await setup_wizard_service.get_progress(session_id)
        
        return {
            "session_id": progress.session_id,
            "current_step": progress.current_step,
            "completed_steps": progress.completed_steps,
            "total_steps": progress.total_steps,
            "progress_percentage": progress.progress_percentage,
            "next_step": progress.next_step,
            "can_proceed": progress.can_proceed,
            "validation_errors": progress.validation_errors
        }
        
    except Exception as e:
        logger.error(f"Error getting setup progress: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting setup progress: {str(e)}")

@router.post("/restaurant-profile/{session_id}")
async def save_restaurant_profile(
    session_id: str,
    profile: RestaurantProfile,
    current_user: Dict = Depends(get_current_user)
):
    """Save restaurant profile (Step 1)"""
    try:
        validation = await setup_wizard_service.save_restaurant_profile(session_id, profile)
        
        return {
            "message": "Restaurant profile saved successfully" if validation.is_valid else "Validation failed",
            "is_valid": validation.is_valid,
            "errors": validation.errors,
            "warnings": validation.warnings,
            "suggestions": validation.suggestions,
            "next_step": SetupStep.MENU_ITEMS if validation.is_valid else None
        }
        
    except Exception as e:
        logger.error(f"Error saving restaurant profile: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving restaurant profile: {str(e)}")

@router.post("/menu-items/{session_id}")
async def save_menu_items(
    session_id: str,
    menu_items: List[MenuItemUpload],
    current_user: Dict = Depends(get_current_user)
):
    """Save menu items (Step 2)"""
    try:
        validation = await setup_wizard_service.save_menu_items(session_id, menu_items)
        
        return {
            "message": "Menu items saved successfully" if validation.is_valid else "Validation failed",
            "is_valid": validation.is_valid,
            "errors": validation.errors,
            "warnings": validation.warnings,
            "suggestions": validation.suggestions,
            "next_step": SetupStep.INGREDIENTS if validation.is_valid else None
        }
        
    except Exception as e:
        logger.error(f"Error saving menu items: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving menu items: {str(e)}")

@router.post("/ingredients/{session_id}")
async def save_ingredients(
    session_id: str,
    ingredients: List[IngredientUpload],
    current_user: Dict = Depends(get_current_user)
):
    """Save ingredients (Step 3)"""
    try:
        validation = await setup_wizard_service.save_ingredients(session_id, ingredients)
        
        return {
            "message": "Ingredients saved successfully" if validation.is_valid else "Validation failed",
            "is_valid": validation.is_valid,
            "errors": validation.errors,
            "warnings": validation.warnings,
            "suggestions": validation.suggestions,
            "next_step": SetupStep.SUPPLIERS if validation.is_valid else None
        }
        
    except Exception as e:
        logger.error(f"Error saving ingredients: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving ingredients: {str(e)}")

@router.post("/suppliers/{session_id}")
async def save_suppliers(
    session_id: str,
    suppliers: List[SupplierUpload],
    current_user: Dict = Depends(get_current_user)
):
    """Save suppliers (Step 4)"""
    try:
        validation = await setup_wizard_service.save_suppliers(session_id, suppliers)
        
        return {
            "message": "Suppliers saved successfully" if validation.is_valid else "Validation failed",
            "is_valid": validation.is_valid,
            "errors": validation.errors,
            "warnings": validation.warnings,
            "suggestions": validation.suggestions,
            "next_step": SetupStep.INITIAL_STOCK if validation.is_valid else None
        }
        
    except Exception as e:
        logger.error(f"Error saving suppliers: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving suppliers: {str(e)}")

@router.post("/initial-stock/{session_id}")
async def save_initial_stock(
    session_id: str,
    initial_stock: List[InitialStockUpload],
    current_user: Dict = Depends(get_current_user)
):
    """Save initial stock (Step 5)"""
    try:
        validation = await setup_wizard_service.save_initial_stock(session_id, initial_stock)
        
        return {
            "message": "Initial stock saved successfully" if validation.is_valid else "Validation failed",
            "is_valid": validation.is_valid,
            "errors": validation.errors,
            "warnings": validation.warnings,
            "suggestions": validation.suggestions,
            "next_step": SetupStep.COMPLETE if validation.is_valid else None
        }
        
    except Exception as e:
        logger.error(f"Error saving initial stock: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving initial stock: {str(e)}")

@router.post("/complete/{session_id}")
async def complete_setup(
    session_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Complete the setup process"""
    try:
        completion = await setup_wizard_service.complete_setup(session_id)
        
        return {
            "message": "Restaurant setup completed successfully",
            "session_id": completion.session_id,
            "restaurant_id": completion.restaurant_id,
            "owner_user_id": completion.owner_user_id,
            "completion_time": completion.completion_time.isoformat(),
            "summary": completion.summary,
            "next_steps": completion.next_steps
        }
        
    except Exception as e:
        logger.error(f"Error completing setup: {e}")
        raise HTTPException(status_code=500, detail=f"Error completing setup: {str(e)}")

@router.post("/upload-csv")
async def upload_csv(
    request: CSVUploadRequest,
    current_user: Dict = Depends(get_current_user)
):
    """Upload CSV data for bulk import"""
    try:
        response = await setup_wizard_service.process_csv_upload(request)
        
        return {
            "success": response.success,
            "records_processed": response.records_processed,
            "records_failed": response.records_failed,
            "errors": response.errors,
            "preview_data": response.preview_data
        }
        
    except Exception as e:
        logger.error(f"Error processing CSV upload: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing CSV upload: {str(e)}")

@router.post("/upload-file")
async def upload_file(
    session_id: str,
    file_type: str,
    file: UploadFile = File(...),
    has_headers: bool = True,
    current_user: Dict = Depends(get_current_user)
):
    """Upload CSV file for bulk import"""
    try:
        # Read file content
        content = await file.read()
        csv_data = content.decode('utf-8')
        
        request = CSVUploadRequest(
            session_id=session_id,
            file_type=file_type,
            csv_data=csv_data,
            has_headers=has_headers
        )
        
        response = await setup_wizard_service.process_csv_upload(request)
        
        return {
            "success": response.success,
            "records_processed": response.records_processed,
            "records_failed": response.records_failed,
            "errors": response.errors,
            "preview_data": response.preview_data
        }
        
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@router.get("/templates/{file_type}")
async def get_csv_template(
    file_type: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get CSV template for data upload"""
    try:
        templates = {
            "menu_items": {
                "headers": ["name", "description", "price", "category"],
                "sample_data": [
                    ["Cappuccino", "Classic Italian coffee drink", "4.50", "Beverages"],
                    ["Grilled Cheese", "Classic grilled cheese sandwich", "8.50", "Food"]
                ],
                "description": "Menu items with name, description, price, and category"
            },
            "ingredients": {
                "headers": ["name", "unit", "current_stock", "min_stock_level", "max_stock_level", "cost_per_unit", "supplier_name"],
                "sample_data": [
                    ["Coffee Beans", "kg", "15.5", "5.0", "50.0", "12.50", "Coffee Bean Co."],
                    ["Milk", "liters", "8.0", "3.0", "20.0", "2.50", "Dairy Delights"]
                ],
                "description": "Ingredients with stock levels, costs, and supplier information"
            },
            "suppliers": {
                "headers": ["name", "contact_person", "email", "phone", "address", "specialties"],
                "sample_data": [
                    ["Coffee Bean Co.", "John Smith", "john@coffeebeanco.com", "+1-555-0101", "456 Coffee St", "Coffee Beans,Sugar"],
                    ["Dairy Delights", "Mary Johnson", "mary@dairydelights.com", "+1-555-0102", "789 Milk Ave", "Milk,Cheese"]
                ],
                "description": "Supplier information with contact details and specialties"
            }
        }
        
        if file_type not in templates:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_type}")
        
        template = templates[file_type]
        
        # Generate CSV content
        csv_content = ",".join(template["headers"]) + "\n"
        for row in template["sample_data"]:
            csv_content += ",".join(str(cell) for cell in row) + "\n"
        
        return {
            "file_type": file_type,
            "description": template["description"],
            "headers": template["headers"],
            "sample_data": template["sample_data"],
            "csv_content": csv_content
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting CSV template: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting CSV template: {str(e)}")

@router.get("/validation/{session_id}/{step}")
async def validate_step(
    session_id: str,
    step: SetupStep,
    current_user: Dict = Depends(get_current_user)
):
    """Validate a specific setup step"""
    try:
        session = await setup_wizard_service.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Validate based on step
        validation = None
        if step == SetupStep.RESTAURANT_PROFILE and session.restaurant_profile:
            validation = await setup_wizard_service._validate_restaurant_profile(session.restaurant_profile)
        elif step == SetupStep.MENU_ITEMS and session.menu_items:
            validation = await setup_wizard_service._validate_menu_items(session.menu_items)
        elif step == SetupStep.INGREDIENTS and session.ingredients:
            validation = await setup_wizard_service._validate_ingredients(session.ingredients)
        elif step == SetupStep.SUPPLIERS and session.suppliers:
            validation = await setup_wizard_service._validate_suppliers(session.suppliers)
        elif step == SetupStep.INITIAL_STOCK and session.initial_stock and session.ingredients:
            validation = await setup_wizard_service._validate_initial_stock(session.initial_stock, session.ingredients)
        else:
            validation = SetupValidation(
                step=step,
                is_valid=False,
                errors=["No data available for validation"]
            )
        
        return {
            "step": validation.step,
            "is_valid": validation.is_valid,
            "errors": validation.errors,
            "warnings": validation.warnings,
            "suggestions": validation.suggestions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating step: {e}")
        raise HTTPException(status_code=500, detail=f"Error validating step: {str(e)}")

@router.delete("/session/{session_id}")
async def delete_setup_session(
    session_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Delete setup wizard session"""
    try:
        # Delete session from Firestore
        db = get_firestore_client()
        db.collection('setup_sessions').document(session_id).delete()
        
        return {
            "message": "Setup session deleted successfully",
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"Error deleting setup session: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting setup session: {str(e)}") 