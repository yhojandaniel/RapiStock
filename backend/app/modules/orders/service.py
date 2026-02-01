from datetime import datetime
from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel import Session, select, extract
from sqlalchemy.orm import selectinload

from backend.app.modules.inventory.models import Product

from backend.app.modules.orders.models import Order, OrderDetail
from backend.app.modules.orders.schemas import OrderCreate, OrderDetailCreate
from backend.app.shared.enums import OrderStatus


class OrderService:
    
    def __init__(self, session: Session):
        self.session = session
        
    def _create_order_item(
        self,
        order_id: UUID,
        item_input: OrderDetailCreate
    ):
        # Select
        product_output = self.session.get(Product, item_input.product_id)
        # Empty?
        if not product_output:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El producto con el código {item_input.product_id} no existe!"
            )
        # Enough stock?
        if product_output.stock < item_input.product_quantity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El producto con el código {item_input.product_id} no tiene suficiente stock!"
            )
        product_output.stock -= item_input.product_quantity
        self.session.add(product_output)
        
        item_output = OrderDetail(
            order_id=order_id,
            product_id=product_output.product_id,
            product_quantity=item_input.product_quantity,
            current_price=product_output.price # Snapshot del precio
        )
        self.session.add(item_output)
    
    def _restore_stock(
        self,
        order: Order
    ):
        # Each product update
        for item in order.details:
            # Get Product
            product = self.session.get(Product, item.product_id)
            if product:
                # Restore
                product.stock += item.product_quantity
                # Added to next commit
                self.session.add(product)
    
    def create_order_as_service(
        self,
        order_input: OrderCreate
    ):
        # Remove details from input
        order_dict = order_input.model_dump(exclude={"details"})
        order_output = Order(**order_dict)
        # Quasi-commit
        self.session.add(order_output)
        self.session.flush()
        self.session.refresh(order_output)
        # validate
        for item_input in order_input.details:
            self._create_order_item(
                order_id=order_output.order_id, 
                item_input=item_input
            )
        # to DB
        self.session.commit()
        self.session.refresh(order_output)
        return order_output
    
    def get_order_as_service(
        self,
        seller_id: UUID | None = None,
        status: OrderStatus | None = None,
        date_from: datetime | None = None, # Note for frontend: Send 00:00:00 here
        date_to: datetime | None = None,   # Note for frontend: Send 23:59:59 here
    ):
        # Query
        order_query = select(Order).options(selectinload(Order.details))
        # Wheres
        if seller_id:
            order_query = order_query.where(Order.seller_id == seller_id)
        if status:
            order_query = order_query.where(Order.status == status)
        # Better for UI
        if date_from:
            order_query = order_query.where(Order.created_at >= date_from)
        if date_to:
            order_query = order_query.where(Order.created_at <= date_to)
        # Run query
        # If there's no data, return []
        return self.session.exec(order_query).all()
    
    def update_order_as_service(
        self,
        order_id: UUID,
        status_input: OrderStatus
    ):
        # Get
        order_output = self.session.get(Order, order_id)
        if not order_output:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El producto con ID:{order_id} no existe!"
            )
        
        # ONLY WORKS TO UPDATE THIS CASE (due current model business)
        # PAID -> CANCELLED
        if status_input == OrderStatus.CANCELLED and order_output.status == OrderStatus.PAID:
            self._restore_stock(order_output)
        # To DB
        order_output.status = status_input
        self.session.add(order_output)
        self.session.commit()
        self.session.refresh(order_output)
        
        return order_output
    
