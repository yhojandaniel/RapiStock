from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional

class SellerBase(SQLModel):
    dni: str = Field(max_length=15, unique=True)
    fullname: str = Field(max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, max_length=100, unique=True)
    is_active: bool = Field(default=True)

class Seller(SellerBase, table=True):
    __tablename__ = "sellers"
    
    seller_id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    modified_at: datetime = Field(default_factory=datetime.now(timezone.utc))