from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

from src.database.models import Role


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=10)


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    role: Role = Role.user
    created_at: datetime
    avatar: str
    active: bool

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"

    class Config:
        from_attributes = True



class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr