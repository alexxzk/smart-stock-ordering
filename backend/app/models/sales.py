from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import date, datetime
import json

class SalesData(BaseModel):
    """Model for individual sales record"""
    date: date
    sales_amount: float = Field(..., gt=0, description="Total daily sales amount")
    orders_count: int = Field(..., ge=0, description="Number of orders for the day")
    menu_items_sold: Dict[str, int] = Field(..., description="Menu items and quantities sold")

class SalesDataUpload(BaseModel):
    """Model for CSV upload response"""
    filename: str
    records_count: int
    date_range: Dict[str, str]
    total_sales: float
    average_daily_sales: float

class ForecastRequest(BaseModel):
    """Model for forecasting request"""
    forecast_days: int = Field(30, ge=1, le=365, description="Number of days to forecast")
    confidence_level: float = Field(0.95, ge=0.8, le=0.99, description="Confidence interval")
    model_type: str = Field("simple", pattern="^(simple|prophet|random_forest)$", description="ML model to use")

class ForecastResult(BaseModel):
    """Model for forecasting results"""
    dates: List[date]
    predicted_sales: List[float]
    predicted_orders: List[int]
    confidence_lower: List[float]
    confidence_upper: List[float]
    model_accuracy: float
    model_type: str
    created_at: datetime

class IngredientRequirement(BaseModel):
    """Model for ingredient requirements"""
    ingredient_name: str
    current_stock: float
    required_amount: float
    pack_size: float
    packs_needed: int
    total_cost: float
    supplier: str
    urgency: str = Field(..., pattern="^(low|medium|high|critical)$")

class SupplierOrder(BaseModel):
    """Model for supplier order"""
    supplier_name: str
    order_items: List[Dict[str, Any]]
    total_cost: float
    delivery_date: Optional[date]
    order_status: str = Field("pending", pattern="^(pending|confirmed|delivered|cancelled)$")
    created_at: datetime
    notes: Optional[str] = None 