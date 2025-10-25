from pydantic import BaseModel
from datetime import datetime
from typing import List, Literal,Optional

# ---------------- Company Schemas ----------------
class CompanyCreate(BaseModel):
    name: str
    whatsapp_number: str
    api_key: str

class CompanyResponse(CompanyCreate):
    id: int

    class Config:
        orm_mode = True

# ---------------- MenuItem Schemas ----------------
class MenuItemCreate(BaseModel):
    name: str
    description: str
    price: float
    available: bool
    category: str

class MenuItemResponse(MenuItemCreate):
    id: int
    company_id: int

    class Config:
        orm_mode = True

# ---------------- Order Item Schemas ----------------
class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int

class OrderItemResponse(BaseModel):
    menu_item_id: int
    quantity: int

    class Config:
        orm_mode = True

# ---------------- Order Schemas ----------------
class OrderCreate(BaseModel):
    customer_name: str
    whatsapp_number: str
    items: List[OrderItemCreate]

class OrderResponse(BaseModel):
    id: int
    customer_name: str
    whatsapp_number: str
    status: str
    created_at: Optional[datetime] = None
    estimated_delivery: Optional[datetime] = None
    items: List[OrderItemResponse]

class OrderStatusUpdate(BaseModel):
    status: Literal["pending", "preparing", "out-for-delivery", "delivered"]
