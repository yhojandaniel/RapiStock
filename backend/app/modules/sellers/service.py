from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel import col, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.sellers.models import Seller
from app.modules.sellers.schemas import SellerCreate, SellerUpdate


class SellerService:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create_seller_as_service(
        self, 
        seller_input: SellerCreate
    ):
        # Input validate
        seller_output = Seller.model_validate(seller_input)
        # Non duplicity
        
        statement_email = select(Seller).where(Seller.email == seller_input.email)
        result_email = await self.session.execute(statement_email)
        if result_email.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El correo ya está registrado!"
            )
            
        statement_dni = select(Seller).where(Seller.dni == seller_input.dni)
        result_dni = await self.session.execute(statement_dni)
        if result_dni.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El dni ya está registrado!"
            )
        # To db
        self.session.add(seller_output)
        await self.session.commit()
        await self.session.refresh(seller_output)
    
        return seller_output
    
    async def get_seller_as_service(
        self,
        seller_id: UUID | None = None,
        fullname: str | None = None,
        dni: str | None = None,
    ):
        seller_query = select(Seller)
        if seller_id:
            seller_query = seller_query.where(Seller.seller_id == seller_id)
        if dni:
            seller_query = seller_query.where(Seller.dni == dni)
        if fullname:
            seller_query = seller_query.where(
                col(Seller.fullname).ilike(f"%{fullname}%")
            )
        # If there's no data, return an empty list
        # Don't use any raise here (v0.1.0)
        result = await self.session.execute(seller_query)
    
        return result.scalars().all()
    
    async def update_seller_as_service(
        self,
        seller_id: UUID,
        seller_data: SellerUpdate,
    ):
        seller_query = await self.session.get(Seller, seller_id)
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
            statement_email = select(Seller).where(
                (Seller.email == new_email) & (Seller.seller_id != seller_id)
            )
            result_email = await self.session.execute(statement_email)
            if result_email.scalars().first():
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El email ya está en uso por otro vendedor")

        # Validación DNI
        if "dni" in seller_dict:
            new_dni = seller_dict["dni"]
            # buscar el mismo dni, para un diferente id (FN)
            statement_dni = select(Seller).where(
                (Seller.dni == new_dni) & (Seller.seller_id != seller_id)
            )
            result_dni = await self.session.execute(statement_dni)
            if result_dni.scalars().first():
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El DNI ya está registrado por otro vendedor")
    
        seller_query.sqlmodel_update(seller_dict)
    
        self.session.add(seller_query)
        await self.session.commit()
        await self.session.refresh(seller_query)
    
        return seller_query
    
    async def delete_seller_as_service(
        self,
        seller_id: UUID 
    ):
        seller_query = await self.session.get(Seller, seller_id)
        if not seller_query:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe un vendedor con el identificador"
            )
        await self.session.delete(seller_query)
        await self.session.commit()
    
        return {"detail": "OK"}
