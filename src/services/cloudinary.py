import hashlib

import asyncio
import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, APIRouter
from concurrent.futures import ThreadPoolExecutor


from src.conf.config import settings

cloud_router = APIRouter(prefix='/cloudinary')

# пул потоків
thread_pool_executor = ThreadPoolExecutor()

class Cloudinary:
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )


    @cloud_router.post("/transform-image")
    async def transform_image(image: bytes):
        # Завантаження в Cloudinary.
        image = await cloudinary.uploader.upload(image)

        # Зміна розміру: 100 у ширину і 50 у висоту.
        transformed_image = await cloudinary.api.transform(
            image["public_id"], width=100, height=50
        )

        # Отримання URL-адреси трансформованого зображення.
        transformed_image_url = cloudinary.utils.url(transformed_image)

        return {"transformed_image_url": transformed_image_url}
    


    # Асинхронна функція завантаження та трансформації зображення
    @staticmethod
    async def upload_and_transform_image_async(image_path, transformation_params):
        loop = asyncio.get_event_loop()
        try:
            response = await loop.run_in_executor(
                thread_pool_executor,
                lambda: cloudinary.uploader.upload(image_path)
            )

            # Трансформація зображення
            transformed_url = cloudinary.CloudinaryImage(response['public_id']).image(transformation_params)

            return transformed_url
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

