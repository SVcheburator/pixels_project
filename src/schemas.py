# src\schemas.py
from datetime import datetime
from src.database.models import Role, User
from typing import List, Optional, Union
from pydantic import BaseModel, Field, EmailStr, ValidationError, validator
from fastapi import UploadFile, Form, File

class UserModel(BaseModel):
    # username: str = Field(min_length=5, max_length=16)
    # email: str
    # password: str = Field(min_length=6, max_length=10)
    ...

class User(BaseModel):
    user: int 
    # email: str
    # password: str 

#     def __get_pydantic_core_schema__(self, handler):
#         custom_schema = {
#             'title': 'User',
#             'type': 'object',
#             'properties': {
#                 'username': {'type': 'string', 'minLength': 5, 'maxLength': 16},
#                 'email': {'type': 'string'},
#                 'password': {'type': 'string', 'minLength': 6, 'maxLength': 10},
#             },
#             'required': ['username', 'email', 'password'],
#         }
#         return custom_schema

# # Генерація схеми
# schema = User.schema()

# # Виведення схеми у консолі
# print(schema)

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

    # class Config:
    #     from_attributes = True

class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RequestEmail(BaseModel):
    email: EmailStr

class CommentBasePost(BaseModel):  # Отримуємо нову назву тут
    comment: str = Field(min_length=1, max_length=255)

class CommentResponse(CommentBasePost):  # А також тут
    id: int
    image_id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True



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





    class Config:
        orm_mode = True


class CommentBase(BaseModel):
    """
    Схема коментарів
    """

    text: str = Field(..., title="Текст")


class CommentList(CommentBase):
    """
    Список комментарів
    """

    class Config:
        orm_mode = True


class CommentBaseCreateUpdate(CommentBase):
    """
    Схема створення/редагування коментарів
    """

    user: int
    post: int


class CommentCreate(CommentBaseCreateUpdate):
    """
    Схема створення коментарів
    """


class CommentUpdate(CommentBaseCreateUpdate):
    """
    Схема зміни коментарів
    """


class TagModel(BaseModel):
    """
    Схема для тегів
    """
    name: str = Field(max_length=25)


# class TagResponse(TagModel):
#     """
#     Схема перетворення при роботі з тегами
#     """
#     id: int

#     class Config:
#         orm_mode = True

# class ImageUploadForm(BaseModel):
#     tags: List[str] = Form([])

#     @validator("tags")
#     def validate_tags(cls, value):
#         if len(value) > 5:
#             raise ValueError("Максимальна кількість тегів - 5")
#         return value