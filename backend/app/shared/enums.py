from enum import Enum

class OrderStatus(str, Enum):
    PAID = "paid"
    REFUNDED = "refunded"

class RefundDetailStatus(str, Enum):
    SAME = "same"     # Vuelve al inventario
    OPENED = "opened" # Se descarta / Merma