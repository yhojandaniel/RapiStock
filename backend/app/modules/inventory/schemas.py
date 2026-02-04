from sqlmodel import SQLModel
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from app.modules.inventory.models import ProductBase

# CREATE: Lo que recibes del Frontend (Sin ID, sin fechas)
class ProductCreate(ProductBase):
    pass

# UPDATE: Todo opcional para PATCH
class ProductUpdate(SQLModel):
    sku: str | None = None
    name: str | None = None
    stock: int | None = None
    price: Decimal | None = None
    is_active: bool | None = None

# READ: Lo que devuelves (Con ID y Fechas)
class ProductRead(ProductBase):
    product_id: UUID
    created_at: datetime
    modified_at: datetime