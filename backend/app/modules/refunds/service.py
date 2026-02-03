

from datetime import datetime
from decimal import Decimal
from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.modules.refunds.models import Refund, RefundDetail
from app.modules.orders.models import Order, OrderDetail
from app.modules.refunds.schemas import RefundCreate
from app.shared.enums import OrderStatus, RefundDetailStatus
from app.modules.inventory.models import Product

VALID_TO_REFUNDS = [OrderStatus.PAID, OrderStatus.REFUNDED]

class RefundService:
    def __init__(self, session: Session):
        self.session = session
        
    def create_refund_as_service(self, refund_input: RefundCreate):
        # Validate data
        order: Order = self.session.get(Order, refund_input.order_id)
        # Order exists
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La orden de compra no existe! Revisa los datos."
            )
        # Only paid orders
        if order.status not in VALID_TO_REFUNDS:
             raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La orden no es apta para reembolso (Debe estar PAID o REFUNDED)."
            )
        total_refunded = Decimal("0.00")
        refund_output = Refund(
            order_id = order.order_id,
            amount=Decimal("0.00") # FOR will increment it
        )
        # Pseudo-commit
        self.session.add(refund_output)
        self.session.flush()
        
        # Items exists
        for item in refund_input.details:
            # Find original order_detail
            order_detail = self.session.get(OrderDetail, item.order_detail_id)
            # Validate owner
            if (not order_detail) or (order_detail.order_id != order.order_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{item.order_detail_id} no pertenece a tu Orden de compra!"
                )
            # Avoid "overrefund"
            if item.product_quantity > order_detail.product_quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"No puedes reembolsar {item.product_quantity}, si ordenaste {order_detail.product_quantity}"
                )
            # Money to be refunded
            total_refunded: Decimal = total_refunded + (order_detail.current_price * item.product_quantity)
            # Check status
            if item.status == RefundDetailStatus.SAME:
                # Get current stock
                product = self.session.get(Product, order_detail.product_id)
                if product:
                    # Restore stock
                    product.stock += item.product_quantity
                    self.session.add(product)
            # If its OPENED, just refund and forget the items refunded as loss
            refund_detail = RefundDetail(
                refund_id=refund_output.refund_id,
                order_detail_id=order_detail.order_detail_id,
                refunded_price=order_detail.current_price,
                product_quantity=item.product_quantity,
                status=item.status
            )
            self.session.add(refund_detail)
        # Save the final amount
        refund_output.amount = total_refunded
        self.session.add(refund_output)
        # Update order status
        order.status = OrderStatus.REFUNDED
        self.session.add(order)
        # To DB
        self.session.commit()
        self.session.refresh(refund_output)
        return refund_output
    
    def get_refund_as_service(
        self, 
        order_id: UUID | None = None, 
        refund_id: UUID | None = None, 
        date_from: datetime | None = None,  # Note for frontend: Send 00:00:00 here
        date_to: datetime | None = None     # Note for frontend: Send 23:59:59 here
    ):
        refund_query = select(Refund).options(selectinload(Refund.details))
        if order_id:
            refund_query = refund_query.where(Refund.order_id == order_id)
        if refund_id:
            refund_query = refund_query.where(Refund.refund_id == refund_id)
        if date_from:
            refund_query = refund_query.where(Refund.created_at >= date_from)
        if date_to:
            refund_query = refund_query.where(Refund.created_at <= date_to)
            
        return self.session.exec(refund_query).all()