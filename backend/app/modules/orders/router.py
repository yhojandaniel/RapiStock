from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from app.shared.dependencies import get_current_user
from app.modules.auth.schemas import TokenData
from app.shared.enums import UserRoleEnum
from app.core.db import SessionDep
from app.modules.orders.schemas import OrderCreate, OrderRead
from app.modules.orders.service import OrderService
from app.shared.enums import OrderStatus

router = APIRouter()

def get_service(session: SessionDep) -> OrderService:
    return OrderService(session=session)

@router.post(
    path="/",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Orders"]
)
async def create_order(
    order_input: OrderCreate,
    service: OrderService = Depends(get_service),
    token_data: TokenData = Depends(get_current_user)
):
    if token_data.role != UserRoleEnum.SELLER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear pedidos"
        )
    order_input.seller_id = token_data.sub_id
    return await service.create_order_as_service(order_input=order_input)

@router.get(
    path="/",
    response_model=list[OrderRead],
    status_code=status.HTTP_200_OK,
    tags=["Orders"]
)
async def get_order(
    seller_id: UUID | None = None,
    status: OrderStatus | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    service: OrderService = Depends(get_service),
    token_data: TokenData = Depends(get_current_user)
):
    current_seller_id = seller_id
    if token_data.role == UserRoleEnum.SELLER:
        current_seller_id = token_data.sub_id
    return await service.get_order_as_service(
        seller_id=current_seller_id,
        status=status,
        date_from=date_from,
        date_to=date_to,
    )

@router.patch(
    path="/{order_id}",
    response_model=OrderRead,
    status_code=status.HTTP_200_OK,
    tags=["Orders"]
)
async def update_order(
    order_id: UUID,
    status_input: OrderStatus,
    service: OrderService = Depends(get_service),
    token_data: TokenData = Depends(get_current_user)
):
    if token_data.role != UserRoleEnum.SELLER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar pedidos"
        )
    return await service.update_order_as_service(
        order_id=order_id,
        seller_id=token_data.sub_id,
        status_input=status_input
    )
