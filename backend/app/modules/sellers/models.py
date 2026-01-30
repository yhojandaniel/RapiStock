from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime, timezone
from pydantic import EmailStr

class SellerBase(SQLModel):
    dni: str = Field(
        max_length=8, 
        unique=True,
        index=True
    )
    fullname: str = Field(
        max_length=150,
        index=True
    )
    phone: str | None = Field(
        default=None, 
        max_length=15
    )
    email: EmailStr | None = Field(
        default=None, 
        max_length=150, 
        unique=True,
        index=True
    )
    is_active: bool = Field(
        default=True
    )

class Seller(SellerBase, table=True):
    __tablename__ = "sellers"
    
    seller_id: UUID | None = Field(
        default_factory=uuid4, 
        primary_key=True
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    modified_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={
            "onupdate": lambda: datetime.now(timezone.utc)
        }
    )