from datetime import datetime

from pydantic import BaseModel, Field


class PostBase(BaseModel):
    """
    Схема опублікування
    """

    image: str = Field(..., title="Світлина")
    text: str = Field(..., title="Текст")


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

    user: int


class PostCreate(PostBaseCreateUpdate):
    """
    Створення посту
    """


class PostUpdate(PostBaseCreateUpdate):
    """
    Редагування посту
    """


class PostSingle(PostBase):
    """
    Публікація при перегляді
    """

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

