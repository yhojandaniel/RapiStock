from datetime import datetime
from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel import select, extract
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.models import Product

from app.modules.orders.models import Order, OrderDetail
from app.modules.orders.schemas import OrderCreate, OrderDetailCreate
from app.shared.enums import OrderStatus


class OrderService:
    
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def _create_order_item(
        self,
        order_id: UUID,
        item_input: OrderDetailCreate
    ):
        # Select
        product_output = await self.session.get(Product, item_input.product_id)
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
            current_price=product_output.price # Snapshot from Orders.price
        )
        self.session.add(item_output)
    
    async def _restore_stock(
        self,
        order: Order
    ):
        # Each product update
        for item in order.details:
            # Get Product
            product = await self.session.get(Product, item.product_id)
            if product:
                # Restore
                product.stock += item.product_quantity
                # Added to next commit
                self.session.add(product)
    
    async def create_order_as_service(
        self,
        order_input: OrderCreate
    ):
        # Remove details from input
        order_dict = order_input.model_dump(exclude={"details"})
        order_output = Order(**order_dict)
        # Quasi-commit
        self.session.add(order_output)
        await self.session.flush()
        await self.session.refresh(order_output)
        # validate
        for item_input in order_input.details:
            await self._create_order_item(
                order_id=order_output.order_id, 
                item_input=item_input
            )
        # to DB
        await self.session.commit()
        # Reload with relationships eager loaded to prevent MissingGreenlet error
        query = select(Order).where(
            Order.order_id == order_output.order_id
        ).options(selectinload(Order.details))
        
        result = await self.session.execute(query)
        order_output = result.scalars().one()
        
        return order_output
    
    async def get_order_as_service(
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
        result = await self.session.execute(order_query)
        # If there's no data, return []
        return result.scalars().all()
    
    async def update_order_as_service(
        self,
        order_id: UUID,
        status_input: OrderStatus
    ):
        # Select without details
        query_order = select(Order).where(Order.order_id == order_id).options(selectinload(Order.details))
        result_query = await self.session.execute(query_order)
        order_output = result_query.scalars().first()
        if not order_output:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El producto con ID:{order_id} no existe!"
            )
        
        # ONLY WORKS TO UPDATE THIS CASE (due current model business)
        # PAID -> CANCELLED
        if status_input == OrderStatus.CANCELLED and order_output.status == OrderStatus.PAID:
            await self._restore_stock(order_output)
        # To DB
        order_output.status = status_input
        self.session.add(order_output)
        await self.session.commit()
        await self.session.refresh(order_output)
        
        return order_output
    
