from sqlmodel import SQLModel
from datetime import datetime
from typing import List
from .models import RefundBase, RefundDetailBase

# DETAILS
class RefundDetailCreate(RefundDetailBase):
    pass

class RefundDetailRead(RefundDetailBase):
    refund_detail_id: int
    refund_id: int

# HEADERS
class RefundCreate(RefundBase):
    details: List[RefundDetailCreate]

class RefundRead(RefundBase):
    refund_id: int
    created_at: datetime