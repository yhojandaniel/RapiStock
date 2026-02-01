from sqlmodel import SQLModel
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import List
from app.shared.enums import OrderStatus
from .models import OrderBase, OrderDetailBase

# Create OrderDetail
class OrderDetailCreate(OrderDetailBase):
    pass 

# Read OrderDetail
class OrderDetailRead(OrderDetailBase):
    order_detail_id: UUID
    order_id: UUID
    current_price: Decimal
    
# Update OrderDetail when something's refunded
# It's not our work here, but refunds task

# Create Order
class OrderCreate(OrderBase):
    # Al crear una orden, generalmente envías los detalles de una vez
    details: List[OrderDetailCreate] 

class OrderRead(OrderBase):
    order_id: UUID
    created_at: datetime
    # Opcional: Podrías incluir los detalles aquí si usas Relationships
    # details: List[OrderDetailRead] = []
    
class OrderUpdate(SQLModel):
    # seller_id: UUID | None = None # cannot be updateable, bcs breaks worksflow
    status: OrderStatus | None = None # <--- AQUÍ está la clave