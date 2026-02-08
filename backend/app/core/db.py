from typing import Annotated
from fastapi import Depends
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.modules.inventory.models import Product
from app.modules.sellers.models import Seller
from app.modules.orders.models import Order, OrderDetail
from app.modules.refunds.models import Refund, RefundDetail

from app.core.config import settings

engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI, 
    echo=True,   # False when u deploy it to prod
    future=True, # Only sqlalchemy v2
    pool_pre_ping=True)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session():
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

# Dependencies registered
SessionDep = Annotated[AsyncSession, Depends(get_session)]