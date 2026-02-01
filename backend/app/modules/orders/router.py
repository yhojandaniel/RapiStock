from datetime import datetime
from fastapi import APIRouter, Depends, status
from uuid import UUID

from backend.app.core.db import SessionDep
from backend.app.modules.orders.schemas import OrderCreate, OrderRead
from backend.app.modules.orders.service import OrderService
from backend.app.shared.enums import OrderStatus

router = APIRouter()

def get_service(session: SessionDep) -> OrderService:
    return OrderService(session=session)

@router.post(
    path="/order",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Orders"]
)
def create_order(
    order_input: OrderCreate,
    service: OrderService = Depends(get_service)
):
    return service.create_order_as_service(order_input=order_input)

@router.get(
    path="/orders",
    response_model=list[OrderRead],
    status_code=status.HTTP_200_OK,
    tags=["Orders"]
)
def get_order(
    seller_id: UUID | None = None,
    status: OrderStatus | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    service: OrderService = Depends(get_service)
):
    return service.get_order_as_service(
        seller_id=seller_id,
        status=status,
        date_from=date_from,
        date_to=date_to
    )

@router.patch(
    path="/order/{order_id}",
    response_model=OrderRead,
    status_code=status.HTTP_200_OK,
    tags=["Orders"]
)
def update_order(
    order_id: UUID,
    status_input: OrderStatus,
    service: OrderService = Depends(get_service)
):
    return service.update_order_as_service(
        order_id=order_id,
        status_input=status_input
    )
