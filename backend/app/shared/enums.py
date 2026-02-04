from enum import Enum

class OrderStatus(str, Enum):
    PAID = "paid"           # Create when its paid
    CANCELLED = "cancelled" # To delete (soft delete)
    REFUNDED = "refunded"   # To ammend (soft partial delete) 

class RefundDetailStatus(str, Enum):
    SAME = "same"     # Vuelve al inventario
    OPENED = "opened" # Se descarta / Merma