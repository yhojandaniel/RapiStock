from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from uuid import UUID
from schemas import SellerCreate, SellerRead, SellerUpdate
from models import Seller
from ...core.db import SessionDep
router = APIRouter()

# Create Seller
@router.post(
    "/seller",
    response_model=SellerRead,
    tags=["Sellers"],
    status_code=status.HTTP_201_CREATED
)
async def create_seller(
    seller_input: SellerCreate, 
    session: SessionDep
):
    # Input validate
    seller_output = Seller.model_validate(seller_input)
    # Non duplicity
    statement_email = select(Seller).where(Seller.email == seller_input.email)
    statement_dni = select(Seller).where(Seller.dni == seller_input.dni)
    if statement_email or statement_dni:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo o el dni ya está registrado, verificar datos!"
        )
    # To DB
    session.add(seller_output)
    session.commit()
    session.refresh(seller_output)
    
    return seller_output

# Get Seller
@router.get(
    "/sellers",
    response_model=list[SellerRead],
    tags=["Sellers"],
    status_code=status.HTTP_200_OK
)
async def get_seller(
    session: SessionDep,
    seller_id: UUID | None = None,
    fullname: str | None = None,
    dni: str | None = None,
):
    seller_query = select(Seller)
    if seller_id:
        seller_query = seller_query.where(Seller.seller_id == seller_id)
    if fullname:
        seller_query = seller_query.where(Seller.fullname == fullname)
    if dni:
        seller_query = seller_query.where(Seller.dni == dni)
    
    seller_output = session.exec(seller_query).all()    
    
    if not seller_output:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND ,
            detail="No se encontró al vendedor con el dato proporcionado"
        )
    
    return seller_output

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
    session: SessionDep
):
    seller_query = session.get(Seller, seller_id)
    if not seller_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existe un vendedor con el identificador"
        )
    
    seller_dict = seller_data.model_dump(exclude_unset=True)
    if not seller_dict:
        return seller_query
    
    # Validación Email
    if "email" in seller_dict:
        new_email = seller_dict["email"]
        # buscar el mismo email, para un diferente id (FN)
        statement = select(Seller).where(
            (Seller.email == new_email) & (Seller.seller_id != seller_id)
        )
        if session.exec(statement).first():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El email ya está en uso por otro vendedor")

    # Validación DNI
    if "dni" in seller_dict:
        new_dni = seller_dict["dni"]
        # buscar el mismo dni, para un diferente id (FN)
        statement = select(Seller).where(
            (Seller.dni == new_dni) & (Seller.seller_id != seller_id)
        )
        if session.exec(statement).first():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El DNI ya está registrado por otro vendedor")
    
    seller_query.sqlmodel_update(seller_dict)
    
    session.add(seller_query)
    session.commit()
    session.refresh(seller_query)
    
    return seller_query

@router.delete(
    "/seller/{seller_id}",
    tags=["Sellers"],
    status_code=status.HTTP_202_ACCEPTED
)
async def delete_seller(
    seller_id: UUID,
    session: SessionDep
):
    seller_query = session.get(Seller, seller_id)
    if not seller_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existe un vendedor con el identificador"
        )
    session.delete(seller_query)
    session.commit()
    
    return {"detail": "OK"}