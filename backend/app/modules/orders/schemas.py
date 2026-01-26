from sqlmodel import SQLModel
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import List
from app.shared.enums import OrderStatus
from .models import OrderBase, OrderDetailBase

# SCHEMAS DE DETALLE
class OrderDetailCreate(OrderDetailBase):
    pass 

class OrderDetailRead(OrderDetailBase):
    order_detail_id: int
    order_id: int

# SCHEMAS DE ORDEN
class OrderCreate(OrderBase):
    # Al crear una orden, generalmente envías los detalles de una vez
    details: List[OrderDetailCreate] 

class OrderRead(OrderBase):
    order_id: int
    created_at: datetime
    # Opcional: Podrías incluir los detalles aquí si usas Relationships
    # details: List[OrderDetailRead] = []
    
class OrderUpdate(SQLModel):
    # Todo es opcional porque es un PATCH
    seller_id: int | None = None
    status: OrderStatus | None = None # <--- AQUÍ está la clave