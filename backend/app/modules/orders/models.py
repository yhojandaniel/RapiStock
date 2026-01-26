from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID
from app.shared.enums import OrderStatus

# ORDER (Padre)
class OrderBase(SQLModel):
    seller_id: int = Field(foreign_key="sellers.seller_id")
    status: OrderStatus = Field(default=OrderStatus.PAID)

class Order(OrderBase, table=True):
    __tablename__ = "orders"
    
    order_id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    modified_at: datetime = Field(default_factory=datetime.now(timezone.utc))

# ORDER DETAIL (Hijo)
class OrderDetailBase(SQLModel):
    product_id: UUID = Field(foreign_key="products.product_id")
    current_price: Decimal = Field(max_digits=10, decimal_places=2)
    product_quantity: int = Field(gt=0) # gt (Greater Than) replica CHECK(> 0)

class OrderDetail(OrderDetailBase, table=True):
    __tablename__ = "order_details"
    
    order_detail_id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.order_id") # FK al padre
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    modified_at: datetime = Field(default_factory=datetime.now(timezone.utc))