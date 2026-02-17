from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_session
from app.shared.enums import UserRoleEnum
from app.modules.auth.schemas import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenData:
    """Decode JWT and return TokenData (no DB hit)."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        sub: str | None = payload.get("sub")
        role: str | None = payload.get("role")
        if sub is None or role is None:
            raise credentials_exception
        token_data = TokenData(sub_id=UUID(sub), role=UserRoleEnum(role))
    except (JWTError, ValueError):
        raise credentials_exception
    return token_data


async def get_current_user_entity(
    token_data: Annotated[TokenData, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Load the full User or Seller entity from DB based on JWT role."""
    from app.modules.auth.models import User
    from app.modules.sellers.models import Seller

    if token_data.role == UserRoleEnum.ADMIN:
        entity = await session.get(User, token_data.sub_id)
    elif token_data.role == UserRoleEnum.SELLER:
        entity = await session.get(Seller, token_data.sub_id)
    else:
        entity = None

    if entity is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return entity


async def get_current_seller(
    token_data: Annotated[TokenData, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Return the authenticated Seller entity or raise 403 if not a seller."""
    from app.modules.sellers.models import Seller

    if token_data.role != UserRoleEnum.SELLER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los vendedores pueden acceder a este recurso",
        )

    seller = await session.get(Seller, token_data.sub_id)
    if seller is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Vendedor no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return seller
