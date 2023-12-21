import hashlib
import logging
import asyncio
import aiohttp
import cloudinary
import cloudinary.uploader
from cloudinary.uploader import upload
from fastapi import HTTPException, APIRouter
from concurrent.futures import ThreadPoolExecutor


from src.conf.config import settings

cloud_router = APIRouter(prefix='/cloudinary')

# пул потоків
thread_pool_executor = ThreadPoolExecutor()

class CloudinaryService:
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )


    @staticmethod
    @cloud_router.post("/transform-image")
    async def transform_image(image: bytes):
        original_image = await cloudinary.uploader.upload(image)

        transformed_image = await cloudinary.uploader.upload(
            original_image["url"],
            width=100,
            height=50,
            public_id=original_image["public_id"] + "_transformed"  
        )

        # Отримання URL-адреси трансформованого зображення.
        transformed_image_url = transformed_image["secure_url"]

        return {"transformed_image_url": transformed_image_url}


    

    # Асинхронна функція завантаження та трансформації зображення
    @classmethod
    async def upload_and_transform_image_async(cls, image_url, transformation_params):
        try:
            result = await upload(
                image_url,
                transformation=transformation_params
            )
            return result['url']
        except Exception as e:
            raise e




    @staticmethod
    def generate_public_id_by_email(email: str, app_name: str = settings.cloudinary_name) -> str:
        try:
            name = hashlib.sha224(email.encode("utf-8")).hexdigest()[:16]
            return f"{app_name}/publication/{name}"
        except Exception as e:
            logging.error(f"Error generating public_id: {e}")
            raise


    @staticmethod
    async def upload_async(file_content, public_id: str, folder="publication"):
        try:
            async with aiohttp.ClientSession() as session:
                # Відправка файлу на сервер Cloudinary
                async with session.post(
                    f"https://api.cloudinary.com/v1_1/{settings.cloudinary_name}/upload",
                    data={"file": file_content, "public_id": public_id, "overwrite": "true"},
                ) as response:
                    return await response.json()
        except Exception as e:
            logging.error(f"Error uploading file to Cloudinary: {e}")
            raise


 
    @staticmethod
    def generate_url(r, public_id) -> str:
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url


    @staticmethod
    def upload_image(image_data: bytes, public_id: str):
        """
        Завантажує зображення на Cloudinary.

        Args:
            image_data: Дані зображення у вигляді байтів.
            public_id: Публічний ідентифікатор для зображення.

        Returns:
            Відповідь від Cloudinary.
        """
        return cloudinary.uploader.upload(
            image_data,
            public_id=public_id,
            overwrite=True,
            folder="transformed_images"
        )