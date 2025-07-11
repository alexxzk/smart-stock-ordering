from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class RestaurantStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

class Restaurant(BaseModel):
    restaurant_id: str
    name: str
    owner_user_id: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    cuisine_type: Optional[str] = None
    status: RestaurantStatus = RestaurantStatus.ACTIVE
    created_at: datetime
    updated_at: datetime
    settings: Dict[str, Any] = Field(default_factory=dict)

class MenuItem(BaseModel):
    item_id: str
    restaurant_id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    cost: Optional[float] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

class RecipeIngredient(BaseModel):
    ingredient_id: str
    quantity: float
    unit: str
    cost_per_unit: Optional[float] = None

class Recipe(BaseModel):
    recipe_id: str
    menu_item_id: str
    restaurant_id: str
    ingredients: List[RecipeIngredient]
    instructions: Optional[str] = None
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None
    servings: Optional[int] = None
    created_at: datetime
    updated_at: datetime

class Ingredient(BaseModel):
    ingredient_id: str
    restaurant_id: str
    name: str
    unit: str
    cost_per_unit: float
    current_stock: float
    min_stock_level: float
    supplier_id: Optional[str] = None
    category: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

class Supplier(BaseModel):
    supplier_id: str
    restaurant_id: str
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    payment_terms: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

class SupplierIngredientLink(BaseModel):
    supplier_id: str
    ingredient_id: str
    restaurant_id: str
    supplier_item_code: Optional[str] = None
    supplier_price: Optional[float] = None
    minimum_order_quantity: Optional[float] = None
    lead_time_days: Optional[int] = None
    is_default: bool = False
    created_at: datetime
    updated_at: datetime

class InitialStock(BaseModel):
    restaurant_id: str
    ingredient_id: str
    initial_quantity: float
    unit: str
    cost_per_unit: float
    supplier_id: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

class RestaurantCreateRequest(BaseModel):
    name: str
    owner_user_id: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    cuisine_type: Optional[str] = None
    settings: Dict[str, Any] = Field(default_factory=dict)

class MenuItemCreateRequest(BaseModel):
    restaurant_id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    cost: Optional[float] = None

class RecipeCreateRequest(BaseModel):
    menu_item_id: str
    restaurant_id: str
    ingredients: List[RecipeIngredient]
    instructions: Optional[str] = None
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None
    servings: Optional[int] = None

class IngredientCreateRequest(BaseModel):
    restaurant_id: str
    name: str
    unit: str
    cost_per_unit: float
    current_stock: float
    min_stock_level: float
    supplier_id: Optional[str] = None
    category: Optional[str] = None

class SupplierCreateRequest(BaseModel):
    restaurant_id: str
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    payment_terms: Optional[str] = None

class InitialStockCreateRequest(BaseModel):
    restaurant_id: str
    ingredient_id: str
    initial_quantity: float
    unit: str
    cost_per_unit: float
    supplier_id: Optional[str] = None
    notes: Optional[str] = None 