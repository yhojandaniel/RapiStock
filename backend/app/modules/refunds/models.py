from uuid import UUID, uuid4
from sqlmodel import Relationship, SQLModel, Field
from datetime import datetime, timezone
from decimal import Decimal
from app.shared.enums import RefundDetailStatus

# REFUND (Base)
class RefundBase(SQLModel):
    order_id: UUID = Field(
        foreign_key="orders.order_id" # FK to get the source order
    )

# REFUNDS (Inheritance)
class Refund(RefundBase, table=True):
    __tablename__ = "refunds"
    
    refund_id: UUID | None = Field(
        default_factory=uuid4, 
        primary_key=True
    )
    amount: Decimal = Field(
        max_digits=10, 
        decimal_places=2
    )
    details: list["RefundDetail"] = Relationship(
        back_populates="refund"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        index=True
    )
    modified_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs = {
            "onupdate": lambda: datetime.now(timezone.utc)
        }
    )

# REFUND DETAIL (Base)
class RefundDetailBase(SQLModel):
    order_detail_id: UUID = Field(
        foreign_key="order_details.order_detail_id"
    )
    product_quantity: int = Field(
        gt=0
    )
    status: RefundDetailStatus = Field(
        default=RefundDetailStatus.SAME,
        index=True
    )

# REFUND DETAILS (Inheritance)
class RefundDetail(RefundDetailBase, table=True):
    __tablename__ = "refund_details"
    
    refund_detail_id: UUID | None = Field(
        default_factory=uuid4, 
        primary_key=True
    )
    refund_id: UUID = Field(
        foreign_key="refunds.refund_id"
    )
    refunded_price: Decimal = Field(
        max_digits=10, 
        decimal_places=2
    )
    refund: "Refund" = Relationship(
        back_populates="details"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    modified_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs = {
            "onupdate": lambda: datetime.now(timezone.utc)
        }
    )