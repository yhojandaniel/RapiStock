from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from fastapi import HTTPException, status
from uuid import UUID

from app.modules.auth.models import User
from app.modules.auth.schemas import UserCreate, UserLogin, Token
from app.modules.sellers.models import Seller
from app.core.security import verify_password, create_access_token, get_password_hash
from app.shared.enums import UserRoleEnum


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session

    # Login user
    async def authenticate_user(self, dni: str, password: str) -> Token:
        statement = select(User).where(User.dni == dni)
        result = await self.session.execute(statement)
        user = result.scalars().first()

        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cuenta desactivada. Contacte al administrador.",
            )

        access_token = create_access_token(
            subject=user.user_id, role=UserRoleEnum.ADMIN
        )
        return Token(access_token=access_token)

    # Login seller
    async def authenticate_seller(self, dni: str, password: str) -> Token:
        statement = select(Seller).where(Seller.dni == dni)
        result = await self.session.execute(statement)
        seller = result.scalars().first()

        if not seller or not verify_password(password, seller.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
            )
        if not seller.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cuenta desactivada. Contacte al administrador.",
            )

        access_token = create_access_token(
            subject=seller.seller_id, role=UserRoleEnum.SELLER
        )
        return Token(access_token=access_token)

    # Create user
    async def create_user(self, user_create: UserCreate) -> User:
        statement_dni = select(User).where(User.dni == user_create.dni)
        result_dni = await self.session.execute(statement_dni)
        if result_dni.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El DNI ya está registrado",
            )

        user_data = user_create.model_dump()
        plain_password = user_data.pop("password")
        user_data["hashed_password"] = get_password_hash(plain_password)
        user_output = User(**user_data)

        self.session.add(user_output)
        await self.session.commit()
        await self.session.refresh(user_output)
        return user_output

    # Soft delete user (sets is_active = False instead of removing the record)
    async def delete_user(self, user_id: UUID) -> dict:
        user = await self.session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El usuario ya está desactivado",
            )
        user.is_active = False
        self.session.add(user)
        await self.session.commit()
        return {"detail": "Usuario desactivado correctamente"}
