from app.modules.auth.models import UserBase
from sqlmodel import SQLModel
from datetime import datetime
from uuid import UUID
from app.shared.enums import UserRoleEnum

# Create
class UserCreate(UserBase):
    password: str

# Login
class UserLogin(SQLModel):
    dni: str
    password: str

# Read
class UserRead(UserBase):
    user_id: UUID
    created_at: datetime
    modified_at: datetime
    
# Token response
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"
    
# Token payload data
class TokenData(SQLModel):
    sub_id: UUID
    role: UserRoleEnum
