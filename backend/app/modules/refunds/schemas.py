from decimal import Decimal
from uuid import UUID
from sqlmodel import SQLModel
from datetime import datetime
from typing import List

from app.shared.enums import RefundDetailStatus
from app.modules.refunds.models import RefundBase, RefundDetailBase

# DETAILS
class RefundDetailCreate(SQLModel):
    order_detail_id: UUID
    product_quantity: int
    status: RefundDetailStatus = RefundDetailStatus.SAME

class RefundDetailRead(RefundDetailBase):
    refund_detail_id: UUID
    refund_id: UUID
    refunded_price: Decimal
    
# No updates here (business model)

# HEADERS
class RefundCreate(RefundBase):
    details: List[RefundDetailCreate]

class RefundRead(RefundBase):
    refund_id: UUID
    amount: Decimal
    created_at: datetime
    details: list[RefundDetailRead]
    
# Neither updates here (business model)