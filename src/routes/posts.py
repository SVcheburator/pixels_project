# src\routes\posts.py
from fastapi import (APIRouter, 
HTTPException, 
UploadFile, 
Depends, File, Form, 
Response, Query)
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import cloudinary.uploader
import cloudinary.api
import os
import shutil
import uuid
from typing import Any, List, Optional
import aiofiles
import logging
from datetime import datetime

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
    UserResponse, 
    UserDb,
    TagModel)
from src.database.db import get_db
from src.services.auth import auth_service
from src.services.posts import PostServices, CommentServices
from src.services.tags import TagServices, Tag
from src.conf.config import settings
from src.services.cloudinary import CloudinaryService
from cloudinary.uploader import upload



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


# публікуємо світлину
@posts_router.post("/publication", response_model=UserResponse, response_model_exclude_unset=True)
async def upload_images_user(
    file: UploadFile = File(),
    text: str = Form(...),
    tags: List[str] = Form([]),
    current_user: UserDb = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    try:
        img_content = await file.read()
        public_id = f"image_{current_user.id}_{uuid.uuid4()}"

        # Завантаження на Cloudinary
        response = cloudinary.uploader.upload(
            img_content,
            public_id=public_id,
            overwrite=True,
            folder="publication"
        )

        # Зберігання в базі даних
        image = Image(
            owner_id=current_user.id,
            url_original=response['secure_url'],
            description=text,
            url_original_qr="",
            updated_at=datetime.now()
        )

        # Розділення тегів та перевірка кількості
        for tags_str in tags:
            tag_list = tags_str.split(',')
            tag_count = len(tag_list)
            print(f"Кількість тегів: {tag_count}")

            if tag_count > 5:
                raise HTTPException(status_code=400, detail="Максимальна кількість тегів - 5")

            for tag_name in tag_list:
                tag_name = tag_name.strip()
                tag = db.query(Tag).filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.add(tag)
                    db.commit()
                    db.refresh(tag)

                image.tags.append(tag)

        db.add(image)
        db.commit()

        user_db = UserDb(**current_user.__dict__)
        return UserResponse(user=user_db)
    except HTTPException as e:
        logging.error(f"Помилка валідації форми: {e}")
        raise
    except Exception as e:
        logging.error(f"Помилка завантаження зображення: {e}")
        raise




# отримаємо списк світлин по ідентифікації користувача
@posts_router.get('/user/{user_id}', response_model=list[PostList])
async def post_list_by_user(user_id: int, 
                            db: Session = Depends(get_db), 
                            user: User = Depends(auth_service.get_current_user)):
    posts = post_services.post_list_by_user(db=db, user_id=user_id)
    if not posts:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Записи не знайдені')
    return JSONResponse(content=[post.json() for post in posts])



# отримувати світлину за унікальним посиланням в БД
@posts_router.get('/{id}', response_model=PostSingle)
async def get_post(id: int, db: Session = Depends(get_db)) -> Any:
    item = await post_services.get_p(db=db, id=id)

    if not item:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Запис не знайдений')

    post_data = {
        'id': item.id,
        'owner_id': item.owner_id,
        'url_original': item.url_original,
        'tags': [],
        'description': item.description,
        'pub_date': item.created_at,
        'img': item.url_original, 
        'text': '',  
        'user': '',  
    }

    return PostSingle(**post_data)



# отримувати світлину за унікальним посиланням в cloudinary
# по аналогії пошуку за параметром в БД, але відповідь "detail": "Not Found"
# @posts_router.get('/post-url/{url_original}', response_model=PostSingle)
# async def get_post_by_url(url_original: str,
#                            db: Session = Depends(get_db),
#                            user: User = Depends(auth_service.get_current_user)):

#     try:
#         item = await post_services.get_post_url(db=db, url_original=url_original)

#         print("Item from the database:", item)  # Додайте це логування

#         if not item:
#             raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Запис не знайдено')

#         post_data = {
#             'id': item.id,
#             'owner_id': item.owner_id,
#             'url_original': item.url_original,
#             'tags': [],  
#             'description': item.description,
#             'pub_date': item.created_at.isoformat(),
#             'img': item.url_original,
#             'text': '',
#             'user': {
#                 'id': user.id,
#                 'username': user.username,
#                 'created_at': user.created_at.isoformat(),
#             },
#         }

#         return JSONResponse(content=post_data)

#     except Exception as e:
#         raise



# отримувати світлину за параметром в БД - працює та повертає значення
@posts_router.get('/post-description/{description}', response_model=PostSingle)
async def get_post_by_description(description: str,
                                   db: Session = Depends(get_db),
                                   user: User = Depends(auth_service.get_current_user)):

    try:
        item = await post_services.get_post_by_description(db=db, description=description)

        if not item:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Запис не знайдено')

        post_data = {
            'id': item.id,
            'owner_id': item.owner_id,
            'url_original': item.url_original,
            'tags': [],  
            'description': item.description,
            'pub_date': item.created_at.isoformat(),
            'img': item.url_original,
            'text': '',
            'user': {
                'id': user.id,
                'username': user.username,
                'created_at': user.created_at.isoformat(),
            },
        }

        return JSONResponse(content=post_data)

    except Exception as e:
        raise



# редагування опису світлини 
@posts_router.put('/{id}', response_model=PostSingle)
async def update_image_description(id: int, description: str, db: Session = Depends(get_db)) -> Any:
    item = await post_services.get_p(db=db, id=id)

    if not item:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Запис не знайдений')

    item.description = description
    db.commit()

    updated_post_data = {
        'id': item.id,
        'owner_id': item.owner_id,
        'url_original': item.url_original,
        'tags': [],
        'description': item.description,
        'pub_date': item.created_at,
        'img': item.url_original, 
        'text': '',  
        'user': '',  
    }

    return PostSingle(**updated_post_data)



# видалення світлини
@posts_router.delete('/{id}', response_model=dict)
async def delete_image(id: int, db: Session = Depends(get_db)) -> dict:
    item = await post_services.get_p(db=db, id=id)

    if not item:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Запись не найдена')
    db.delete(item)
    db.commit()

    return {"message": "Запис видалено успішно"}
