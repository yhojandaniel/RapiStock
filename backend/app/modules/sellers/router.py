from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from app.core.db import SessionDep
from app.modules.sellers.schemas import SellerCreate, SellerRead, SellerUpdate
from app.modules.sellers.models import Seller
from app.modules.sellers.service import SellerService
from app.shared.dependencies import get_current_user, get_current_seller
from app.modules.auth.schemas import TokenData
from app.shared.enums import UserRoleEnum

router = APIRouter()

def get_service(session: SessionDep) -> SellerService:
    return SellerService(session=session)

# Create Seller
@router.post(
    "/",
    response_model=SellerRead,
    tags=["Sellers"],
    status_code=status.HTTP_201_CREATED
)
async def create_seller(
    seller_input: SellerCreate,
    service: SellerService = Depends(get_service),
    token_data: TokenData = Depends(get_current_user)
):
    if token_data.role != UserRoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear vendedores"
        )
    return await service.create_seller_as_service(seller_input=seller_input)

# Get Sellers
@router.get(
    "/",
    response_model=list[SellerRead],
    tags=["Sellers"],
    status_code=status.HTTP_200_OK
)
async def get_seller(
    service: SellerService = Depends(get_service),
    token_data: TokenData = Depends(get_current_user),
    seller_id: UUID | None = None,
    fullname: str | None = None,
    dni: str | None = None,
):
    if token_data.role != UserRoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para obtener vendedores"
        )
    return await service.get_seller_as_service(
        seller_id=seller_id, 
        fullname=fullname, 
        dni=dni
    )
    
# Get me as seller
@router.get(
    "/me",
    response_model=SellerRead,
    tags=["Sellers"],
    status_code=status.HTTP_200_OK,
)
async def get_me_as_seller(
    current_seller: Seller = Depends(get_current_seller),
):
    return current_seller

# Update Seller (admin only)
@router.patch(
    "/{seller_id}",
    response_model=SellerRead,
    tags=["Sellers"],
    status_code=status.HTTP_200_OK
)
async def update_seller(
    seller_id: UUID,
    seller_data: SellerUpdate,
    service: SellerService = Depends(get_service),
    token_data: TokenData = Depends(get_current_user),
):
    if token_data.role != UserRoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar vendedores"
        )
    return await service.update_seller_as_service(
        seller_id=seller_id, 
        seller_data=seller_data
    )

# Delete seller
@router.delete(
    "/{seller_id}",
    tags=["Sellers"],
    status_code=status.HTTP_202_ACCEPTED
)
async def delete_seller(
    seller_id: UUID,
    service: SellerService = Depends(get_service),
    token_data: TokenData = Depends(get_current_user),
):
    if token_data.role != UserRoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar vendedores"
        )
    return await service.delete_seller_as_service(seller_id=seller_id)