from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional
from datetime import datetime

class OrderRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    items: List[Dict[str, int]] = Field(..., description="List of items and quantities to order")
    notes: Optional[str] = Field(None, description="Optional notes for the order")

class OrderResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    order_id: str
    status: str
    created_at: datetime
    message: Optional[str] = None 