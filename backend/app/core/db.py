from typing import Annotated
from fastapi import Depends, FastAPI
from sqlmodel import Session, create_engine, SQLModel

from app.modules.inventory.models import Product
from app.modules.sellers.models import Seller
from app.modules.orders.models import Order, OrderDetail
# from app.modules.refunds.models import Refund

sqlite_name = "dev_rapistock.db"
sqlite_url = f"sqlite:///{sqlite_name}"
connect_args = {"check_same_thread": False}

engine = create_engine(sqlite_url, connect_args=connect_args)

def create_all_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# Registramos la dependencia de la sesión
SessionDep = Annotated[Session, Depends(get_session)]