from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, List, Optional, Any
from datetime import date, datetime
from enum import Enum

class SaleItem(BaseModel):
    """Model for individual sale item with ingredient tracking"""
    model_config = ConfigDict(protected_namespaces=())
    
    menu_item_id: str
    menu_item_name: str
    quantity: int = Field(..., gt=0, description="Quantity sold")
    unit_price: float = Field(..., gt=0, description="Price per unit")
    total_price: float = Field(..., gt=0, description="Total price for this item")
    ingredients_used: Dict[str, float] = Field(default_factory=dict, description="Ingredients and quantities used")

class SalesRecord(BaseModel):
    """Model for sales record with automatic ingredient deduction"""
    model_config = ConfigDict(protected_namespaces=())
    
    sale_id: str
    restaurant_id: str
    date: date
    timestamp: datetime
    items: List[SaleItem]
    total_sales_amount: float = Field(..., gt=0, description="Total sales amount")
    total_items_sold: int = Field(..., ge=0, description="Total number of items sold")
    ingredients_deducted: Dict[str, float] = Field(default_factory=dict, description="Total ingredients deducted")
    low_stock_warnings: List[str] = Field(default_factory=list, description="Ingredients below minimum stock")
    created_at: datetime
    updated_at: datetime

class IngredientDeduction(BaseModel):
    """Model for ingredient deduction tracking"""
    model_config = ConfigDict(protected_namespaces=())
    
    ingredient_id: str
    ingredient_name: str
    quantity_deducted: float
    unit: str
    previous_stock: float
    new_stock: float
    min_stock_level: float
    is_low_stock: bool
    deduction_timestamp: datetime

class LowStockWarning(BaseModel):
    """Model for low stock warnings"""
    model_config = ConfigDict(protected_namespaces=())
    
    ingredient_id: str
    ingredient_name: str
    current_stock: float
    min_stock_level: float
    unit: str
    urgency: str = Field(..., pattern="^(low|medium|high|critical)$")
    warning_timestamp: datetime
    is_resolved: bool = False

class SalesCreateRequest(BaseModel):
    """Model for creating a new sales record"""
    model_config = ConfigDict(protected_namespaces=())
    
    restaurant_id: str
    date: date
    items: List[SaleItem]
    notes: Optional[str] = None

class SalesUpdateRequest(BaseModel):
    """Model for updating a sales record"""
    model_config = ConfigDict(protected_namespaces=())
    
    items: Optional[List[SaleItem]] = None
    notes: Optional[str] = None

class IngredientStockUpdate(BaseModel):
    """Model for updating ingredient stock levels"""
    model_config = ConfigDict(protected_namespaces=())
    
    ingredient_id: str
    new_stock: float
    reason: str = Field(..., description="Reason for stock update (sale, restock, adjustment, etc.)")
    notes: Optional[str] = None

class StockAdjustment(BaseModel):
    """Model for manual stock adjustments"""
    model_config = ConfigDict(protected_namespaces=())
    
    ingredient_id: str
    adjustment_amount: float = Field(..., description="Positive for addition, negative for deduction")
    reason: str = Field(..., description="Reason for adjustment")
    notes: Optional[str] = None
    adjustment_timestamp: datetime

class IngredientUsageReport(BaseModel):
    """Model for ingredient usage reporting"""
    model_config = ConfigDict(protected_namespaces=())
    
    ingredient_id: str
    ingredient_name: str
    total_used: float
    unit: str
    usage_period: str
    average_daily_usage: float
    current_stock: float
    min_stock_level: float
    days_until_stockout: Optional[float] = None
    last_restock_date: Optional[date] = None

class SalesAnalytics(BaseModel):
    """Model for sales analytics with ingredient tracking"""
    model_config = ConfigDict(protected_namespaces=())
    
    period_start: date
    period_end: date
    total_sales: float
    total_items_sold: int
    top_selling_items: List[Dict[str, Any]]
    ingredient_usage_summary: List[IngredientUsageReport]
    low_stock_alerts: List[LowStockWarning]
    revenue_by_category: Dict[str, float]
    average_order_value: float
    peak_sales_hours: List[int] 