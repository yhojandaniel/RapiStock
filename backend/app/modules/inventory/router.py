from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import select
from uuid import UUID
from app.modules.inventory.service import ProductService
from app.modules.inventory.schemas import ProductCreate, ProductRead, ProductUpdate
from app.modules.inventory.models import Product
from app.core.db import SessionDep
from app.shared.dependencies import get_current_user
from app.modules.auth.schemas import TokenData
from app.shared.enums import UserRoleEnum
router = APIRouter()

def get_service(session: SessionDep) -> ProductService:
    return ProductService(session=session)

@router.post(
    "/",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Products"]
)
async def create_product(
    product_input: ProductCreate, 
    service: ProductService = Depends(get_service),
    token_data: TokenData = Depends(get_current_user)
    ):
    if token_data.role != UserRoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear productos"
        )
    return await service.create_product_as_service(product_input=product_input)

@router.get(
    "/",
    response_model=list[ProductRead],
    status_code=status.HTTP_200_OK,
    tags=["Products"]
)
async def get_product(
    service: ProductService = Depends(get_service),
    search: str | None = None, 
    offset: int = 0,
    limit: int = Query(default=20, ge=1, le=100),
    token_data: TokenData = Depends(get_current_user)
):
    return await service.get_product_as_service(search=search, offset=offset, limit=limit)

@router.patch(
    "/{product_id}",
    response_model=ProductRead,
    status_code=status.HTTP_200_OK,
    tags=["Products"]
)
async def update_product(
    product_id: UUID, 
    product_input: ProductUpdate, 
    service: ProductService = Depends(get_service),
    token_data: TokenData = Depends(get_current_user)
):
    if token_data.role != UserRoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar productos"
        )
    return await service.update_product_as_service(product_id=product_id, product_input=product_input)

@router.delete(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    tags=["Products"]
)
async def delete_product(
    product_id: UUID,
    service: ProductService = Depends(get_service),
    token_data: TokenData = Depends(get_current_user)
):
    if token_data.role != UserRoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar productos"
        )
    return await service.delete_product_as_service(product_id=product_id)
