from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from uuid import UUID
from schemas import ProductCreate, ProductRead, ProductUpdate
from models import Product
from ...core.db import SessionDep
router = APIRouter()

@router.post(
    "/product",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Products"]
)
async def create_product(
    product_input: ProductCreate, 
    session: SessionDep):
    # Validate
    product_output = Product.model_validate(product_input)
    # Non duplicity
    statement_sku = select(Product).where(Product.sku == product_input.sku)
    statement_name = select(Product).where(Product.name == product_input.name)
    if statement_sku or statement_name:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Ya existe un producto registrado con ese Nombre o SKU"
        )
    # To DB
    session.add(product_output)
    session.commit()
    session.refresh(product_output)
    return product_output

@router.get(
    "/products",
    response_model=list[ProductRead],
    status_code=status.HTTP_200_OK,
    tags=["Products"]
)
async def get_product(
    session: SessionDep,
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
    product_output = session.exec(product_query).all()
    # DB drop something?
    if not product_output:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay productos con ese nombre o SKU"
        )
    
    return product_output

@router.patch(
    "/product/{product_id}",
    response_model=ProductRead,
    status_code=status.HTTP_200_OK,
    tags=["Products"]
)
async def update_product(
    product_id: int, 
    product_input: Product, 
    session:SessionDep
):
    # Validate
    product_query = session.get(Product, product_id)
    if not product_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El producto que quieres modificar no existe!"
        )
    # Empty?
    product_dict = product_input.model_dump(exclude_unset=True)
    if not product_dict:
        return product_query
    # Which?
    if "sku" in product_dict:
        new_sku = product_dict["sku"]
        statement = select(Product).where(
            (Product.sku == new_sku) & 
            (Product.product_id != product_id)
            )
        if session.exec(statement).first():
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
        if session.exec(statement).first():
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
    session.add(product_query)
    session.commit()
    session.refresh(product_query)
    
    return product_query

@router.delete(
    "/product/{product_id}",
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Products"]
)
async def create_product(
    product_id: UUID,
    session: SessionDep
):
    # Validate
    product_query = session.get(Product, product_id)
    # Some?
    if not product_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El producto que quieres borrar no existe con ese ID!"
        )
    # to DB
    session.delete(product_query)
    session.commit()
    return {"detail": "OK"}