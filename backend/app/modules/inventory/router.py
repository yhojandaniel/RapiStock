from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from uuid import UUID
from app.modules.inventory.service import ProductService
from app.modules.inventory.schemas import ProductCreate, ProductRead, ProductUpdate
from app.modules.inventory.models import Product
from app.core.db import SessionDep
router = APIRouter()

def get_service(session: SessionDep) -> ProductService:
    return ProductService(session=session)

@router.post(
    "/product",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Products"]
)
async def create_product(
    product_input: ProductCreate, 
    service: ProductService = Depends(get_service),
    ):
    return service.create_product_as_service(product_input=product_input)

@router.get(
    "/products",
    response_model=list[ProductRead],
    status_code=status.HTTP_200_OK,
    tags=["Products"]
)
async def get_product(
    service: ProductService = Depends(get_service),
    search: str | None = None, 
):
    return service.get_product_as_service(search=search)

@router.patch(
    "/product/{product_id}",
    response_model=ProductRead,
    status_code=status.HTTP_200_OK,
    tags=["Products"]
)
async def update_product(
    product_id: UUID, 
    product_input: ProductUpdate, 
    service: ProductService = Depends(get_service),
):
    return service.update_product_as_service(product_id=product_id, product_input=product_input)

@router.delete(
    "/product/{product_id}",
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Products"]
)
async def delete_product(
    product_id: UUID,
    service: ProductService = Depends(get_service),
):
    return service.delete_product_as_service(product_id=product_id)
