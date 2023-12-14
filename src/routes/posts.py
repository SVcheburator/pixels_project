# src\routes\posts.py
from fastapi import APIRouter, HTTPException, UploadFile, Depends, File, Form
import cloudinary.uploader
import cloudinary.api
import os
import shutil
import uuid
from typing import Any, List, Optional
import aiofiles

from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette import status
from starlette.status import HTTP_404_NOT_FOUND

from src.database.models import User, Image, Comment
from src.schemas import (
    CommentCreate, 
    CommentList, 
    PostCreate, 
    PostList, 
    PostSingle, 
    TagModel)
from src.database.db import get_db
from src.services.auth import auth_service
from src.services.posts import PostServices, CommentServices
from src.services.tags import TagServices, Tag
from src.conf.config import settings



class Cloudinary:
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )

posts_router = APIRouter(prefix='/posts')
tags_router = APIRouter(prefix='/tags')

tag_services = TagServices(Tag)
post_services = PostServices(Image)
comment_services = CommentServices(Comment)



@posts_router.get('/user/{user_id}', response_model=list[PostList])
async def post_list_by_user(user_id: int, 
                            db: Session = Depends(get_db), 
                            user: User = Depends(auth_service.get_current_user)):
    """
    Список світлин
    """
    posts = await post_services.post_list_by_user(db=db, user_id=user_id)
    if not posts:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Записи не знайдені')
    return posts

UPLOADS_DIR = "uploads"
MAX_FILE_SIZE = 100000000  # максимальний розмір файлу в байтах


def save_file_sync(file, destination):
    file_size = 0
    with open(destination, "wb") as file_object:
        while True:
            chunk = file.read(1024)
            if not chunk:
                break
            file_size += len(chunk)
            if file_size > MAX_FILE_SIZE:
                raise HTTPException(status_code=413, detail="File size is over the limit")
            file_object.write(chunk)


@posts_router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_post(
    img: UploadFile = File(...),
    db: Session = Depends(get_db),
    text: str = Form(...),
    tags: Optional[List[TagModel]] = Form(None),
    user: User = Depends(auth_service.get_current_user),
):
    """
    Створення світлини
    """

    try:
        # Зберігання файлу в теку uploads
        file_path = os.path.join(UPLOADS_DIR, f'{uuid.uuid4()}{img.filename}')

        save_file_sync(img.file, file_path)

        # Зберігання інформації про фото в базу даних
        post_in = PostCreate(text=text, user=user.id, img=file_path)
        created_post = await post_services.create_post(db=db, post_data=post_in, file_path=file_path)

        # Додаємо теги до створеної публікації, якщо вони передані
        if tags is not None:
            created_tags = await tag_services.create_or_get_tags(db=db, tag_data=tags[:5])
            created_post.tags.extend(created_tags)

        db.commit()
        return created_post
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@posts_router.get('/{id}', response_model=PostSingle)
async def get_post(id: int, db: Session = Depends(get_db)) -> Any:
    """
    Отримання світлини
    """
    item = post_services.get_p(db=db, id=id)
    if not item:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Запись не найдена')
    return item



@posts_router.get('/{post_id}/comments', response_model=list[CommentList])
async def comment_list_by_post(post_id: int, db: Session = Depends(get_db)):
    """
    Список світлин
    """
    comments = await comment_services.comments_by_post(db=db, post_id=post_id)
    if not comments:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Комментарии не найдены')
    return comments



@posts_router.post('/{post_id}/comments/create', status_code=status.HTTP_201_CREATED)
async def create_comment(
    *,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
    comment_in: CommentCreate,
    post_id: int
):
    """
    Створення коментаря
    """
    comment_in.post_id = post_id  # Змінено post на post_id
    return await comment_services.create_comment(db=db, obj_in=comment_in)




@posts_router.put('/{id}', response_model=PostSingle)
async def update_image_description(
    id: int,
    description: str,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    Редагування опису світлини
    """
    try:
        # Використання оновленого сервісу для оновлення опису
        updated_post = await post_services.update_p(db=db, obj_in=dict(id=id, text=description))
        
        return updated_post
    except Exception as e:
        # Обробка помилок
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@posts_router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(id: int, db: Session = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    Видалення світлини
    """
    post = post_services.get_p(db=db, id=id)
    if not post:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Запис не знайдений')
    
    # Перевірка, чи користувач є власником світлини
    if post.user != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Ви не маєте прав для видалення цієї світлини')
    
    await post_services.remove_p(db=db, id=id)
