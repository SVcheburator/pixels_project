from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Union
from fastapi import UploadFile

from src.database.models import Role


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=10)


class UserModelCaptcha(UserModel):
    h_captcha_response: str = Field(alias="h-captcha-response")


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    role: Role = Role.user
    created_at: datetime
    avatar: str
    active: bool

    class ConfigDict:
        from_attributes = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"

    # class ConfigDict:
    #     from_attributes = True


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr


class CommentBase(BaseModel):
    comment: str = Field(min_length=1, max_length=255)


class CommentResponse(CommentBase):
    id: int
    image_id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class ConfigDict:
        from_attributes = True


class UserRole(BaseModel):
    role: Role


class RequestUserName(BaseModel):
    username: str = Field(min_length=5, max_length=16)


class User(BaseModel):
    user: int 

class PostCreate(BaseModel):
    """
    Створення посту
    """
    text: str
    user: int
    img: UploadFile
    description: str

    class Config:
        orm_mode = True


class PostBase(BaseModel):
    """
    Схема опублікування
    """
    img: str
    text: str
    user: int
    # img: str = Field(..., title="Світлина")
    # text: str = Field(..., title="Текст")
    # tags: Optional[List[str]] = None
    # user: Optional[int] = None


    class Config:
        from_attributes = True


class PostList(PostBase):
    """
    Публікації в списку
    """

    pub_date: datetime = Field(..., title="Дата публикации")

    class Config:
        orm_mode = True


class PostBaseCreateUpdate(PostBase):
    """
    Схема створення/редагування посту
    """
    user: Union[User, int]

class PostCreate(PostBaseCreateUpdate):
    """
    Створення посту
    """
    user: int


class PostUpdate(PostBaseCreateUpdate):
    """
    Редагування посту
    """


class PostSingle(PostBase):
    img: str
    text: str
    user: str
    id: int
    owner_id: int
    url_original: str
    tags: List[str]
    description: Optional[str]
    pub_date: datetime

    class Config:
        orm_mode = True


class TagModel(BaseModel):
    """
    Схема для тегів
    """
    name: str = Field(max_length=25)
class UpdateProfile(BaseModel):
    username: str | None = Field(min_length=5, max_length=16)


class UpdateFullProfile(UpdateProfile):
    is_active: bool | None = None
    role: Role | None = None
