from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import Image
from src.services.cloudinary import cloudinary 
import cloudinary
from cloudinary.uploader import upload
import cloudinary.api
import qrcode
from io import BytesIO
import cloudinary.utils

from fastapi import APIRouter, Depends
from src.conf.config import settings

class CloudinaryService:
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )

cloud_router = APIRouter(prefix='', tags=["Cloudinary image operations"])


@cloud_router.get("/transformed_image/{image_id}")
def transform_and_update_image(image_id: str, angle: int = 45, db: Session = Depends(get_db)):
    """
    The transform_and_update_image function takes an image_id and angle as input,
        transforms the original image by rotating it by the specified angle,
        uploads the transformed image to Cloudinary, and updates the database with 
        a new url for that transformed image.
    
    :param image_id: str: Identify the image to be transformed
    :param angle: int: Specify the angle by which the image should be rotated
    :param db: Session: Get the database session
    :return: The following:
    :doc-author: Trelent
    """
    image = db.query(Image).filter(Image.id == image_id).first()
    print("1:", image)
    print("Start:", image_id)

    if image:
        url_original = image.url_original
        public_id = cloudinary.utils.cloudinary_url(url_original)[0].split("/")[-1]
        print("Start URL:", url_original)

        folder_path = "transform"
        transformation = {"angle": angle}

        public_id = f"{folder_path}/{public_id}"

        response = upload(url_original, transformation=transformation, public_id=public_id)

        transformed_image_url = response['secure_url']

        db.query(Image).filter(Image.id == image_id).update({"url_transformed": transformed_image_url})
        db.commit()

        print("1:", image_id)
        print("Original Image URL:", url_original)
        print("Transformed Image URL:", transformed_image_url)

        return {"message": f"Image transformed and updated successfully. Rotated by {angle} degrees.",
                "transformed_image_url": transformed_image_url}

    return {"error": "Image not found."}



@cloud_router.get("/qr_codes_image/{image_id}")
def qr_codes_and_update_image(image_id: str, db: Session = Depends(get_db)):
    """
    The qr_codes_and_update_image function generates a QR code for the original image and updates the database with it.
    
    
    :param image_id: str: Pass the image id to the function
    :param db: Session: Access the database
    :return: The following:
    :doc-author: Trelent
    """
    image = db.query(Image).filter(Image.id == image_id).first()
    print("1:", image)
    print("Start:", image_id)

    if image:
        url_original = image.url_original
        public_id = cloudinary.utils.cloudinary_url(url_original)[0].split("/")[-1]
        print("Start URL:", url_original)

        folder_path = "qr_codes"

        # Create QR 
        qr_original = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr_original.add_data(url_original)
        qr_original.make(fit=True)

        # Save QR 
        qr_code_original_image = qr_original.make_image(fill_color="black", back_color="white")
        qr_code_original_image_io = BytesIO()
        qr_code_original_image.save(qr_code_original_image_io, format="PNG")

        # Upload QR 
        qr_code_original_response = upload(
            qr_code_original_image_io.getvalue(),
            folder=folder_path,
            public_id=f"{folder_path}/{public_id}_qr_code",
            format="png",
            overwrite=True
        )

        qr_code_original_url = qr_code_original_response['secure_url']

        db.query(Image).filter(Image.id == image_id).update({"url_original_qr": qr_code_original_url})
        db.commit()

        print("1:", image_id)
        print("Original Image URL:", url_original)
        print("QR Code URL for Original Image:", qr_code_original_url)

        return {"message": f"QR Code generated and updated successfully for the original image.",
                "url_original_qr": qr_code_original_url}

    return {"error": "Image not found."}


@cloud_router.get("/qr_codes_transformed_image/{image_id}")
def qr_codes_and_update_transformed_image(image_id: str, db: Session = Depends(get_db)):
    """
    The qr_codes_and_update_transformed_image function generates a QR code for the transformed image and updates the url_transformed_qr field in the database.
    
    :param image_id: str: Get the image from the database
    :param db: Session: Get the database session
    :return: A dictionary with the url_transformed_qr key
    :doc-author: Trelent
    """
    image = db.query(Image).filter(Image.id == image_id).first()

    if image:
        if not image.url_transformed:
            # Якщо url_transformed пустий, викликаємо transform_and_update_image
            transform_and_update_image(image_id=image_id, db=db)

        url_transformed = image.url_transformed
        public_id = cloudinary.utils.cloudinary_url(url_transformed)[0].split("/")[-1]

        folder_path = "qr_codes"

        # Створення QR-коду
        qr_transformed = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr_transformed.add_data(url_transformed)
        qr_transformed.make(fit=True)

        # Збереження QR-коду
        qr_code_transformed_image = qr_transformed.make_image(fill_color="navy", back_color="lightyellow")
        qr_code_transformed_image_io = BytesIO()
        qr_code_transformed_image.save(qr_code_transformed_image_io, format="PNG")

        # Завантаження QR-коду
        qr_code_transformed_response = upload(
            qr_code_transformed_image_io.getvalue(),
            folder=folder_path,
            public_id=f"{folder_path}/{public_id}_qr_code_transformed",
            format="png",
            overwrite=True
        )

        qr_code_transformed_url = qr_code_transformed_response['secure_url']

        image = db.query(Image).filter(Image.id == image_id).first()
        # Оновлення поля url_transformed_qr у базі даних
        db.query(Image).filter(Image.id == image_id).update({"url_transformed_qr": qr_code_transformed_url})
        db.commit()

        return {"message": f"QR Code generated and updated successfully for the transformed image.",
                "url_transformed_qr": qr_code_transformed_url}

    return {"error": "Image not found."}

