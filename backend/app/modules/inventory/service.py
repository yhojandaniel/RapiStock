from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel import select, col, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.models import Product
from app.modules.inventory.schemas import ProductCreate, ProductUpdate

class ProductService:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create_product_as_service(
        self,
        product_input: ProductCreate,
    ):
        # Validate
        product_output = Product.model_validate(product_input)
        # Non duplicity
        
        statement_sku = select(Product).where(Product.sku == product_input.sku)
        result_sku = await self.session.execute(statement_sku)
        
        if result_sku.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="Ya existe un producto registrado con ese mismo SKU!"
            )
            
        statement_name = select(Product).where(Product.name == product_input.name)
        result_name = await self.session.execute(statement_name)
        
        if result_name.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="Ya existe un producto registrado con ese mismo nombre!"
            )
        
        # To DB
        self.session.add(product_output)
        await self.session.commit()
        await self.session.refresh(product_output)
        
        return product_output
    
    async def get_product_as_service(
        self,
        search: str | None = None, 
    ):
        # Query
        product_query = select(Product)
        # Where
        if search:
            product_query = product_query.where(
                or_(
                    col(Product.sku).ilike(f"%{search}%"),
                    col(Product.name).ilike(f"%{search}%")
                )
            )
        # If there's no data, return empty list
        # Don't use any raise here (v0.1.0)
        
        result = await self.session.execute(product_query)
        return result.scalars().all()
    
    async def update_product_as_service(
        self,
        product_id: UUID, 
        product_input: ProductUpdate, 
    ):
        # Validate
        product_query = await self.session.get(Product, product_id)
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
            sku_result = await self.session.execute(statement)
            if sku_result.scalars().first():
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
            name_result = await self.session.execute(statement)
            if name_result.scalars().first():
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
        await self.session.commit()
        await self.session.refresh(product_query)
    
        return product_query
    
    async def delete_product_as_service(
        self,
        product_id: UUID,
    ):
        # Query
        product_query = await self.session.get(Product, product_id)
        # Found?
        if not product_query:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El producto que quieres borrar no existe con ese ID!"
            )
        # to DB
        await self.session.delete(product_query)
        await self.session.commit()
        return {"detail": "OK"}