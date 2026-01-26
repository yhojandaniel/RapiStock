from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from decimal import Decimal
from app.shared.enums import RefundDetailStatus

# REFUND (Padre)
class RefundBase(SQLModel):
    order_id: int = Field(foreign_key="orders.order_id")
    amount: Decimal = Field(max_digits=10, decimal_places=2)

class Refund(RefundBase, table=True):
    __tablename__ = "refunds"
    
    refund_id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    modified_at: datetime = Field(default_factory=datetime.now(timezone.utc))

# REFUND DETAIL (Hijo)
class RefundDetailBase(SQLModel):
    order_detail_id: int = Field(foreign_key="order_details.order_detail_id")
    refunded_price: Decimal = Field(max_digits=10, decimal_places=2)
    product_quantity: int = Field(gt=0)
    status: RefundDetailStatus = Field(default=RefundDetailStatus.SAME)

class RefundDetail(RefundDetailBase, table=True):
    __tablename__ = "refund_details"
    
    refund_detail_id: int | None = Field(default=None, primary_key=True)
    refund_id: int = Field(foreign_key="refunds.refund_id")
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    modified_at: datetime = Field(default_factory=datetime.now(timezone.utc))