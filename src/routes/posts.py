# pixels_project\src\routes\posts.py
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

import shutil
import uuid
from typing import Any
from typing import List

from sqlalchemy.orm import Session
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
# from src.services.core import create_p, get_p, update_p, remove_p
from src.services.posts import PostServices, CommentServices
from src.services.tags import TagServices, Tag


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




@posts_router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_post(
    *,
    img: UploadFile = File(...),
    db: Session = Depends(get_db),
    text: str = Form(...),
    tags: List[TagModel] = Form(...),
    user: User = Depends(auth_service.get_current_user),
):
    """
    Створення світлини
    """
    # Змінено шлях до зображення на URL-рядок
    url = f'media/{uuid.uuid4()}{img.filename}'
    
    try:
        with open(url, "wb") as buffer:
            shutil.copyfileobj(img.file, buffer)
    finally:
        img.file.close()
    
    # Використання PostCreate для передачі даних в сервіс
    post_in = PostCreate(text=text, image=url, user=user.id)
    
    # Використання оновленого сервісу для створення публікації
    created_post = await post_services.create_p(db=db, obj_in=post_in)
    
    # Додаємо теги до створеної публікації
    # якщо прибрати з конструкції [:5], обмеження зникне
    created_tags = await tag_services.create_or_get_tags(db=db, tag_data=tags[:5]) 
    created_post.tags.extend(created_tags)
    db.commit()

    return created_post


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
    *, db: Session = Depends(get_db), user: User = Depends(auth_service.get_current_user), 
    comment_in: CommentCreate, post_id: int
):
    """
    Створення коментаря
    """
    comment_in.post = post_id
    return await post_services.create_p(db=db, obj_in=comment_in)



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
    post = post_services.get_p(db=db, id=id)
    if not post:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Запись не найдена')
    
    # Перевірка, чи користувач є власником світлини
    if post.user != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Ви не маєте прав для редагування цієї світлини')
    
    post.text = description
    return await post_services.update_p(db=db, obj_in=post)




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