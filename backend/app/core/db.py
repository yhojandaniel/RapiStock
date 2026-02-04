from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, create_engine, SQLModel

from app.modules.inventory.models import Product
from app.modules.sellers.models import Seller
from app.modules.orders.models import Order, OrderDetail
from app.modules.refunds.models import Refund, RefundDetail

from app.core.config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)

def create_all_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# Dependencies registered
SessionDep = Annotated[Session, Depends(get_session)]