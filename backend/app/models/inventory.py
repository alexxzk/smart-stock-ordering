from pydantic import BaseModel, Field
from typing import Optional

class InventoryItem(BaseModel):
    item_id: str
    name: str
    current_stock: float = Field(..., description="Current stock level")
    min_stock: float = Field(..., description="Minimum stock level before reorder")
    pack_size: float = Field(..., description="Supplier pack size")
    supplier: Optional[str] = None 