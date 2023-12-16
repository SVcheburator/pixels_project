import cloudinary
from cloudinary.uploader import upload
from src.conf.config import settings
from src.services.cloudinary import CloudinaryService
from PIL import Image, ImageFilter
import qrcode
import os

class Cloudinary:
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )


def apply_filters(image_path, output_path, filters=None, size=None):
    # Відкрийте зображення
    image = Image.open(image_path)

    # Застосуйте фільтри
    if filters:
        for f in filters:
            image = image.filter(f)

    # Змініть розмір зображення
    if size:
        image = image.resize(size)

    # Збережіть оброблене зображення
    image.save(output_path)

def create_qr_code(url_original, output_path):
    # Створіть QR-код
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url_original)
    qr.make(fit=True)

    # Створіть зображення QR-коду
    img = qr.make_image(fill_color="black", back_color="white")

    # Збережіть зображення QR-коду
    img.save(output_path)


if __name__ == "__main__":
    # Приклад використання
    image_path = r"C:\Users\Work\Desktop\cocktail-dog — копия.jpg"
    output_image_path = r"D:\1\1.jpg"
    filters_to_apply = [ImageFilter.BLUR]  # Залиште тільки BLUR, якщо хочете лише розмиття
    new_size = (800, 500)
    url_original = "https://example.com"
    output_qr_path = os.path.join(r"D:\1", "qr_code.png")  # Змінено цей рядок

    # Обробіть зображення
    apply_filters(image_path, output_image_path, filters=filters_to_apply, size=new_size)

    # Створіть QR-код
    create_qr_code(url_original, output_qr_path)




    
# def upload_image_to_cloudinary(file_path: str, public_id: str) -> dict:
#     # Параметри завантаження
#     upload_options = {
#         "public_id": public_id,
#     }

#     # Завантаження зображення
#     result = upload(file_path, **upload_options)

#     # Повернення результатів
#     return result

# # Приклад використання
# file_path = "C:\\Users\\Work\\Desktop\\cocktail-dog.jpg"
# public_id = "unique_public_id_for_image"

# # Завантаження зображення на Cloudinary
# upload_result = upload_image_to_cloudinary(file_path, public_id)

# # Виведення результатів
# print(upload_result)