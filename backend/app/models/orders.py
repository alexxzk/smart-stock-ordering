from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class OrderRequest(BaseModel):
    items: List[Dict[str, int]] = Field(..., description="List of items and quantities to order")
    notes: Optional[str] = Field(None, description="Optional notes for the order")

class OrderResponse(BaseModel):
    order_id: str
    status: str
    created_at: datetime
    message: Optional[str] = None 