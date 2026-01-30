from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime, timezone
from decimal import Decimal

# BASE
class ProductBase(SQLModel):
    sku: str = Field(
        max_length=50, 
        unique=True, 
        index=True
    )
    name: str = Field(
        max_length=150, 
        index=True
    )
    stock: int = Field(
        default=0, 
        ge=0
    ) 
    price: Decimal = Field(
        default=0, 
        max_digits=10, 
        decimal_places=2, 
        ge=0 # ge=0 [CHECK(stock >= 0)]
    )
    is_active: bool = Field(
        default=True
    )

# TABLA (Database)
class Product(ProductBase, table=True):
    __tablename__ = "products"
    
    product_id: UUID = Field(
        default_factory=uuid4, 
        primary_key=True
    )
    created_at: datetime = Field(
        default_factory = lambda: datetime.now(timezone.utc)
    )
    modified_at: datetime = Field(
        default_factory = lambda: datetime.now(timezone.utc),
        sa_column_kwargs={
            "onupdate": lambda: datetime.now(timezone.utc)
        }
    )