from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from uuid import UUID

from app.core.db import SessionDep
from app.modules.auth.schemas import UserCreate, UserLogin, Token, TokenData, UserRead
from app.modules.auth.service import AuthService
from app.shared.dependencies import get_current_user, get_current_seller
from app.shared.enums import UserRoleEnum

router = APIRouter()


def get_service(session: SessionDep) -> AuthService:
    return AuthService(session=session)

# Login
@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_service)
):
    return await service.authenticate_user(form_data.username, form_data.password)


@router.post("/sellers/login", response_model=Token)
async def seller_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_service)
):
    return await service.authenticate_seller(form_data.username, form_data.password)


# Get me
@router.get(
    "/me", 
    response_model=TokenData, 
    tags=["Auth"], 
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)]
)
async def get_me(token_data: TokenData = Depends(get_current_user)):
    return token_data


# Create user
@router.post(
    "/create", response_model=UserRead,
    tags=["Auth"],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)]
)
async def create_user(
    user_create: UserCreate,
    service: AuthService = Depends(get_service),
    token_data: TokenData = Depends(get_current_user)
):
    if token_data.role != UserRoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear usuarios"
        )
    return await service.create_user(user_create)

# Delete user
@router.delete(
    "/delete/{user_id}",
    response_model=dict,
    tags=["Auth"],
    status_code=status.HTTP_202_ACCEPTED
)
async def delete_user(
    user_id: UUID,
    service: AuthService = Depends(get_service),
    token_data: TokenData = Depends(get_current_user)
):
    if token_data.role != UserRoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar usuarios"
        )
    return await service.delete_user(user_id)
