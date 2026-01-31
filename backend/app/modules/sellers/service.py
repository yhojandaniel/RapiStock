from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel import Session, select

from backend.app.modules.sellers.models import Seller
from backend.app.modules.sellers.schemas import SellerCreate, SellerUpdate


class SellerService:
    def __init__(self, session: Session):
        self.session = session
        
    def create_seller_as_service(
        self, 
        seller_input: SellerCreate
    ):
        # Input validate
        seller_output = Seller.model_validate(seller_input)
        # Non duplicity
        statement_email = select(Seller).where(
            Seller.email == seller_input.email
        )
        statement_dni = select(Seller).where(
            Seller.dni == seller_input.dni
        )
        
        if self.session.exec(statement_email).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El correo ya está registrado!"
            )
        if self.session.exec(statement_dni).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El dni ya está registrado!"
            )
        # To db
        self.session.add(seller_output)
        self.session.commit()
        self.session.refresh(seller_output)
    
        return seller_output
    
    def get_seller_as_service(
        self,
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
    
        seller_output = self.session.exec(seller_query).all()    
    
        # If there's no data, return an empty list
    
        return seller_output
    
    def update_seller_as_service(
        self,
        seller_id: UUID,
        seller_data: SellerUpdate,
    ):
        seller_query = self.session.get(Seller, seller_id)
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
            if self.session.exec(statement).first():
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El email ya está en uso por otro vendedor")

        # Validación DNI
        if "dni" in seller_dict:
            new_dni = seller_dict["dni"]
            # buscar el mismo dni, para un diferente id (FN)
            statement = select(Seller).where(
                (Seller.dni == new_dni) & (Seller.seller_id != seller_id)
            )
            if self.session.exec(statement).first():
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El DNI ya está registrado por otro vendedor")
    
        seller_query.sqlmodel_update(seller_dict)
    
        self.session.add(seller_query)
        self.session.commit()
        self.session.refresh(seller_query)
    
        return seller_query
    
    def delete_seller_as_service(
        self,
        seller_id: UUID 
    ):
        seller_query = self.session.get(Seller, seller_id)
        if not seller_query:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe un vendedor con el identificador"
            )
        self.session.delete(seller_query)
        self.session.commit()
    
        return {"detail": "OK"}
