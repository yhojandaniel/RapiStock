from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from uuid import UUID
from app.core.db import SessionDep
from app.modules.sellers.schemas import SellerCreate, SellerRead, SellerUpdate
from app.modules.sellers.models import Seller
from app.modules.sellers.service import SellerService

router = APIRouter()

def get_service(session: SessionDep) -> SellerService:
    return SellerService(session=session)

# Create Seller
@router.post(
    "/seller",
    response_model=SellerRead,
    tags=["Sellers"],
    status_code=status.HTTP_201_CREATED
)
async def create_seller(
    seller_input: SellerCreate,
    service: SellerService = Depends(get_service),
):
    return service.create_seller_as_service(seller_input=seller_input)

# Get Seller
@router.get(
    "/sellers",
    response_model=list[SellerRead],
    tags=["Sellers"],
    status_code=status.HTTP_200_OK
)
async def get_seller(
    service: SellerService = Depends(get_service),
    seller_id: UUID | None = None,
    fullname: str | None = None,
    dni: str | None = None,
):
    return service.get_seller_as_service(
        seller_id=seller_id, 
        fullname=fullname, 
        dni=dni
    )

# Update Seller
@router.patch(
    "/seller/{seller_id}",
    response_model=SellerRead,
    tags=["Sellers"],
    status_code=status.HTTP_200_OK
)
async def update_seller(
    seller_id: UUID,
    seller_data: SellerUpdate,
    service: SellerService = Depends(get_service),
):
    return service.update_seller_as_service(seller_id=seller_id, seller_data=seller_data)

@router.delete(
    "/seller/{seller_id}",
    tags=["Sellers"],
    status_code=status.HTTP_202_ACCEPTED
)
async def delete_seller(
    seller_id: UUID,
    service: SellerService = Depends(get_service),
):
    return service.delete_seller_as_service(seller_id=seller_id)