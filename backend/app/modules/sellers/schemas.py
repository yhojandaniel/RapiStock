from sqlmodel import SQLModel
from uuid import UUID
from datetime import datetime
from .models import SellerBase

class SellerCreate(SellerBase):
    pass

class SellerUpdate(SQLModel):
    dni: str | None = None
    fullname: str | None = None
    phone: str | None = None
    email: str | None = None
    is_active: bool | None = None

class SellerRead(SellerBase):
    seller_id: UUID
    created_at: datetime
    modified_at: datetime