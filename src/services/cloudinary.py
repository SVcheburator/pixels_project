import hashlib
import logging
import asyncio
import aiohttp
import cloudinary
import cloudinary.uploader
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


 
    # @staticmethod
    # def generate_public_id_by_email(email: str, app_name: str = settings.cloudinary_name) -> str:
    #     name = hashlib.sha224(email.encode("utf-8")).hexdigest()[:16]
    #     return f"{app_name}/publication/{name}"



    def generate_url(r, public_id) -> str:
        src_url = cloudinary.CloudinaryImage(public_id)\
        .build_url(
            width=250, height=250, crop="fill", version=r.get("version") # type: ignore
        )
        return src_url