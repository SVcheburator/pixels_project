import cloudinary
from cloudinary.uploader import upload
from src.conf.config import settings
from src.services.cloudinary import CloudinaryService


class Cloudinary:
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )



def upload_image_to_cloudinary(file_path: str, public_id: str) -> dict:


    # Параметри завантаження
    upload_options = {
        "public_id": public_id,
    }

    # Завантаження зображення
    result = upload(file_path, **upload_options)

    # Повернення результатів
    return result

# Приклад використання
file_path = "C:\\Users\\Work\\Desktop\\cocktail-dog.jpg"
public_id = "unique_public_id_for_image"

# Завантаження зображення на Cloudinary
upload_result = upload_image_to_cloudinary(file_path, public_id)

# Виведення результатів
print(upload_result)