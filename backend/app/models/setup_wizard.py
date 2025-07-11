from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Dict, List, Optional, Any
from datetime import datetime, date
from enum import Enum

class SetupStep(str, Enum):
    """Enum for setup wizard steps"""
    RESTAURANT_PROFILE = "restaurant_profile"
    MENU_ITEMS = "menu_items"
    INGREDIENTS = "ingredients"
    SUPPLIERS = "suppliers"
    INITIAL_STOCK = "initial_stock"
    COMPLETE = "complete"

class RestaurantProfile(BaseModel):
    """Model for restaurant profile setup"""
    model_config = ConfigDict(protected_namespaces=())
    
    name: str = Field(..., min_length=1, description="Restaurant name")
    address: str = Field(..., description="Restaurant address")
    phone: str = Field(..., description="Contact phone number")
    email: EmailStr = Field(..., description="Contact email")
    owner_email: EmailStr = Field(..., description="Owner email for account creation")
    owner_name: str = Field(..., description="Owner full name")
    cuisine_type: Optional[str] = Field(None, description="Type of cuisine")
    business_hours: Optional[Dict[str, str]] = Field(None, description="Business hours")
    tax_rate: Optional[float] = Field(0.0, ge=0, le=1, description="Tax rate as decimal")
    currency: str = Field("USD", description="Currency code")

class MenuItemUpload(BaseModel):
    """Model for menu item upload"""
    model_config = ConfigDict(protected_namespaces=())
    
    name: str = Field(..., description="Menu item name")
    description: Optional[str] = Field(None, description="Item description")
    price: float = Field(..., gt=0, description="Item price")
    category: str = Field(..., description="Item category")
    is_available: bool = Field(True, description="Item availability")
    ingredients: List[Dict[str, Any]] = Field(..., description="Recipe ingredients")

class IngredientUpload(BaseModel):
    """Model for ingredient upload"""
    model_config = ConfigDict(protected_namespaces=())
    
    name: str = Field(..., description="Ingredient name")
    unit: str = Field(..., description="Unit of measurement")
    current_stock: float = Field(0.0, ge=0, description="Current stock level")
    min_stock_level: float = Field(..., gt=0, description="Minimum stock level")
    max_stock_level: Optional[float] = Field(None, gt=0, description="Maximum stock level")
    cost_per_unit: float = Field(..., ge=0, description="Cost per unit")
    supplier_name: Optional[str] = Field(None, description="Supplier name")

class SupplierUpload(BaseModel):
    """Model for supplier upload"""
    model_config = ConfigDict(protected_namespaces=())
    
    name: str = Field(..., description="Supplier name")
    contact_person: str = Field(..., description="Contact person name")
    email: EmailStr = Field(..., description="Contact email")
    phone: str = Field(..., description="Contact phone")
    address: str = Field(..., description="Supplier address")
    specialties: List[str] = Field(default_factory=list, description="Supplier specialties")
    payment_terms: Optional[str] = Field(None, description="Payment terms")
    delivery_schedule: Optional[str] = Field(None, description="Delivery schedule")

class InitialStockUpload(BaseModel):
    """Model for initial stock upload"""
    model_config = ConfigDict(protected_namespaces=())
    
    ingredient_id: str = Field(..., description="Ingredient ID")
    quantity: float = Field(..., gt=0, description="Initial stock quantity")
    cost: float = Field(..., ge=0, description="Total cost of initial stock")
    supplier_id: Optional[str] = Field(None, description="Supplier ID")
    notes: Optional[str] = Field(None, description="Additional notes")

class SetupWizardSession(BaseModel):
    """Model for setup wizard session"""
    model_config = ConfigDict(protected_namespaces=())
    
    session_id: str = Field(..., description="Unique session ID")
    restaurant_id: Optional[str] = Field(None, description="Restaurant ID once created")
    current_step: SetupStep = Field(SetupStep.RESTAURANT_PROFILE, description="Current setup step")
    completed_steps: List[SetupStep] = Field(default_factory=list, description="Completed steps")
    restaurant_profile: Optional[RestaurantProfile] = Field(None, description="Restaurant profile data")
    menu_items: List[MenuItemUpload] = Field(default_factory=list, description="Menu items data")
    ingredients: List[IngredientUpload] = Field(default_factory=list, description="Ingredients data")
    suppliers: List[SupplierUpload] = Field(default_factory=list, description="Suppliers data")
    initial_stock: List[InitialStockUpload] = Field(default_factory=list, description="Initial stock data")
    created_at: datetime = Field(default_factory=datetime.now, description="Session creation time")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update time")
    is_completed: bool = Field(False, description="Setup completion status")

class SetupProgress(BaseModel):
    """Model for setup progress tracking"""
    model_config = ConfigDict(protected_namespaces=())
    
    session_id: str
    current_step: SetupStep
    completed_steps: List[SetupStep]
    total_steps: int = 5
    progress_percentage: float
    next_step: Optional[SetupStep]
    can_proceed: bool
    validation_errors: List[str] = Field(default_factory=list)

class CSVUploadRequest(BaseModel):
    """Model for CSV upload requests"""
    model_config = ConfigDict(protected_namespaces=())
    
    session_id: str = Field(..., description="Setup session ID")
    file_type: str = Field(..., description="Type of data being uploaded")
    csv_data: str = Field(..., description="CSV data as string")
    has_headers: bool = Field(True, description="Whether CSV has headers")

class CSVUploadResponse(BaseModel):
    """Model for CSV upload response"""
    model_config = ConfigDict(protected_namespaces=())
    
    success: bool
    records_processed: int
    records_failed: int
    errors: List[str] = Field(default_factory=list)
    preview_data: List[Dict[str, Any]] = Field(default_factory=list)

class SetupValidation(BaseModel):
    """Model for setup validation"""
    model_config = ConfigDict(protected_namespaces=())
    
    step: SetupStep
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)

class SetupCompletion(BaseModel):
    """Model for setup completion"""
    model_config = ConfigDict(protected_namespaces=())
    
    session_id: str
    restaurant_id: str
    owner_user_id: str
    completion_time: datetime
    summary: Dict[str, Any]
    next_steps: List[str] = Field(default_factory=list) 