from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from app.core.db import SessionDep
from app.modules.refunds.schemas import RefundCreate, RefundRead
from app.modules.refunds.service import RefundService
from app.shared.enums import RefundDetailStatus, UserRoleEnum
from app.shared.dependencies import get_current_user
from app.modules.auth.schemas import TokenData

router = APIRouter()

def get_service(session: SessionDep) -> RefundService:
    return RefundService(session=session)

@router.post(
    path="/",
    response_model=RefundRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Refunds"]
)
async def create_refund(
    refund_input: RefundCreate,
    service: RefundService = Depends(get_service),
    token_data: TokenData = Depends(get_current_user)
):
    if token_data.role != UserRoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear reembolsos"
        )
    return await service.create_refund_as_service(refund_input=refund_input)

@router.get(
    path="/",
    response_model=list[RefundRead],
    status_code=status.HTTP_200_OK,
    tags=["Refunds"]
)
async def get_refund(
    order_id: UUID | None = None,
    refund_id: UUID | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    service: RefundService = Depends(get_service),
    token_data: TokenData = Depends(get_current_user)
):
    if token_data.role != UserRoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para obtener reembolsos"
        )
    return await service.get_refund_as_service(
        order_id=order_id,
        refund_id=refund_id,
        date_from=date_from,
        date_to=date_to
    )

# No updates due business model
""" 
@router.patch(
    path="/{order_id}",
    response_model=RefundRead,
    status_code=status.HTTP_200_OK,
    tags=["Orders"]
)
def update_order(
    order_id: UUID,
    status_input: RefundDetailStatus,
    service: RefundService = Depends(get_service)
):
    return service.update_order_as_service(
        order_id=order_id,
        status_input=status_input
    )
"""
