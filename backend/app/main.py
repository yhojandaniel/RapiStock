from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Resources
from app.core.db import create_all_tables

# Routers
from app.modules.inventory.router import router as inventory_router
from app.modules.orders.router import router as orders_router
from app.modules.refunds.router import router as refunds_router
from app.modules.sellers.router import router as sellers_router
# from app.modules.refunds.router import router as refunds_router

# Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Turn on
    print("Iniciando RapiStock API...")
    # create all tables
    create_all_tables()
    
    yield # API's alive!
    
    # Turn off
    print("Apagando RapiStock API...")
    # Aquí podrías cerrar conexiones a Redis, enviar logs finales, etc.

# App
app = FastAPI(
    title="RapiStock API",
    description="API para gestión de inventario y órdenes multitienda.",
    version="0.1.0",
    lifespan=lifespan, # lifespan linked with top statement
)


# ACL for frontend sources
origins = [
    "http://localhost:5173",  # Vite (React/Vue)
    "http://localhost:3000",  # Next.js / Create React App
    "http://127.0.0.1:5173",  # Unlike de IP local
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allow GET, POST, PUT, DELETE, PATCH, etc.
    allow_headers=["*"], # Allow auth tokens and headers custom
)

# Routers list
app.include_router(
    inventory_router, 
    prefix="/products",
    tags=["Products"]
)
app.include_router(
    orders_router, 
    prefix="/orders",
    tags=["Orders"]
)
app.include_router(
    sellers_router, 
    prefix="/sellers",
    tags=["Sellers"]
)
app.include_router(
    refunds_router,
    prefix="/refunds",
    tags=["Refunds"]
)


# Home
@app.get("/", tags=["Health"])
def read_root():
    return {"status": "ok", "message": "RapiStock API is running!!"}