from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.modules.inventory.models import Product
from app.modules.inventory.schemas import ProductCreate, ProductUpdate

class ProductService:
    def __init__(self, session: Session):
        self.session = session
        
    def create_product_as_service(
        self,
        product_input: ProductCreate,
    ):
        # Validate
        product_output = Product.model_validate(product_input)
        # Non duplicity
        statement_sku = select(Product).where(Product.sku == product_input.sku)
        statement_name = select(Product).where(Product.name == product_input.name)
        
        if self.session.exec(statement_sku).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="Ya existe un producto registrado con ese mismo SKU!"
            )
        if self.session.exec(statement_name).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="Ya existe un producto registrado con ese mismo nombre!"
            )
        
        # To DB
        self.session.add(product_output)
        self.session.commit()
        self.session.refresh(product_output)
        
        return product_output
    
    def get_product_as_service(
        self,
        name: str | None = None, 
        sku: str | None = None,
    ):
        # Query
        product_query = select(Product)
        # Where
        if name:
            product_query = product_query.where(Product.name == name)
        if sku:
            product_query = product_query.where(Product.sku == sku)
        product_output = self.session.exec(product_query).all()
        # If there's no data, return empty list
    
        return product_output
    
    def update_product_as_service(
        self,
        product_id: UUID, 
        product_input: ProductUpdate, 
    ):
        # Validate
        product_query = self.session.get(Product, product_id)
        if not product_query:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El producto que quieres modificar no existe!"
            )
        # Empty?
        product_dict = product_input.model_dump(exclude_unset=True)
        if not product_dict:
            return product_query
        # Which were modified?
        if "sku" in product_dict:
            new_sku = product_dict["sku"]
            statement = select(Product).where(
                (Product.sku == new_sku) & 
                (Product.product_id != product_id)
            )
            if self.session.exec(statement).first():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya hay un producto con ese SKU!"
                )
    
        if "name" in product_dict:
            new_name = product_dict["name"]
            statement = select(Product).where(
                (Product.name == new_name) & 
                (Product.product_id != product_id)
            )
            if self.session.exec(statement).first():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya hay un producto con ese nombre!"
                )
            
        if "stock" in product_dict:
            new_stock = product_dict["stock"]
            if new_stock < 0:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="El stock tiene que ser igual o mayor que cero!"
                )
            
        if "price" in product_dict:
            new_price = product_dict["price"]
            if new_price <= 0:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="El precio tiene que ser mayor que cero!"
                )           
    
        # To db
        product_query.sqlmodel_update(product_dict)
        self.session.add(product_query)
        self.session.commit()
        self.session.refresh(product_query)
    
        return product_query
    
    def delete_product_as_service(
        self,
        product_id: UUID,
    ):
        # Query
        product_query = self.session.get(Product, product_id)
        # Found?
        if not product_query:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El producto que quieres borrar no existe con ese ID!"
            )
        # to DB
        self.session.delete(product_query)
        self.session.commit()
        return {"detail": "OK"}