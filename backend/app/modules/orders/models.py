from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4
from app.shared.enums import OrderStatus

# ORDER (Base): data input from user
class OrderBase(SQLModel):
    seller_id: UUID = Field(
        foreign_key="sellers.seller_id", # FK from Sellers
        index=True
    )
    status: OrderStatus = Field(
        default=OrderStatus.PAID,
        index=True
    )

# ORDERS (Inheritance)
class Order(OrderBase, table=True):
    __tablename__ = "orders"
    
    order_id: UUID | None = Field(
        default_factory=uuid4, 
        primary_key=True
    )
    details: list["OrderDetail"] = Relationship(
        back_populates="order"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        index=True
    )
    modified_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={
            "onupdate": lambda: datetime.now(timezone.utc)
        }
    )

# ORDER DETAIL (Base): Data input from user
class OrderDetailBase(SQLModel):
    product_id: UUID = Field(
        foreign_key="products.product_id" # FK from Products
    )
    product_quantity: int = Field(
        gt=0 # gt (Greater Than) same CHECK(> 0)
    ) 

# ORDER DETAILS (Inheritance)
class OrderDetail(OrderDetailBase, table=True):
    __tablename__ = "order_details"
    
    order_detail_id: UUID | None = Field(
        default_factory=uuid4,
        primary_key=True
    )
    order_id: UUID = Field(
        foreign_key="orders.order_id", # FK from Orders
        index=True
    )
    current_price: Decimal = Field(
        max_digits=10, 
        decimal_places=2,
        # gt here? research
    )
    order: "Order" = Relationship(
        back_populates="details"
    )
    created_at: datetime = Field(
        default_factory = lambda: datetime.now(timezone.utc)
    )
    modified_at: datetime = Field(
        default_factory = lambda: datetime.now(timezone.utc),
        sa_column_kwargs = {
            "onupdate": lambda: datetime.now(timezone.utc)
        }
    )