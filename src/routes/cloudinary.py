from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import FileResponse
from PIL import Image as PILImage
from io import BytesIO
from datetime import datetime

import uuid
import qrcode
import requests
from sqlalchemy.orm import Session
from src.database.models import Image as DBImage
from src.database.db import get_db
from src.services.cloudinary import CloudinaryService
from src.services.auth import auth_service
from src.schemas import UserDb
import cloudinary.uploader

cloud_router = APIRouter(prefix='/cloudinary')


@cloud_router.get("/transformed_image/{image_id}")
async def get_transformed_image(image_id: str, db: Session = Depends(get_db)):
    image = get_image_by_id(db, image_id)

    if not image:
        raise HTTPException(status_code=404, detail='Image not found')

    # Download the image from Cloudinary
    cloudinary_url = image.url_original
    response = requests.get(cloudinary_url)
    print(cloudinary_url)

    if response.status_code == 200:
        file_path = f"uploads/{image_id}_original.jpg"
        with open(file_path, "wb") as file:
            file.write(response.content)

        return file_path
    raise HTTPException(status_code=response.status_code, detail='Failed to download original image')


async def process_image(image_id: str,
                        db: Session = Depends(get_db),
                        current_user: UserDb = Depends(auth_service.get_current_user)):
    # Step 1: Call get_transformed_image
    original_image_path = await get_transformed_image(image_id, db)

    # Step 2: Call transform with UploadFile and owner_id
    owner_id = current_user.id
    transformed_data = await transform(owner_id=owner_id, file=original_image_path, db=db)

    return transformed_data


async def transform(owner_id: int,
                    file: UploadFile = File(...),
                    description: str = "", db: Session = Depends(get_db)):

    # Check if it's a file path or an UploadFile object
    if isinstance(file, str):
        # If it's a file path, read the content
        with open(file, "rb") as file_content:
            img_content = file_content.read()
    else:
        # If it's an UploadFile object, read the content
        img_content = await file.read()

    # Transform the image
    image = PILImage.open(BytesIO(img_content))
    image = image.resize((400, 400))
    image = image.convert("RGB")
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    transformed_image_data = buffer.getvalue()

    # Generate a unique public_id for Cloudinary
    public_id = f"transformed_image_{uuid.uuid4()}"

    try:
        print(f"Public ID before upload: {public_id}")

        # Завантаження на Cloudinary
        response = cloudinary.uploader.upload(
            img_content,
            public_id=public_id,
            overwrite=True,
            folder="transformed_image"
        )
        
        print("Successfully uploaded to Cloudinary")

        # Get the URL of the transformed image from Cloudinary
        transformed_image_url = response['secure_url']

        # Save information about the transformed image to the database
        db_image = DBImage(
            owner_id=owner_id,
            url_original="Original image URL" if image.url_original else None,
            url_transformed=transformed_image_url,
            url_original_qr="Original image QR URL" if image.url_original_qr else None,
            url_transformed_qr="Transformed image QR URL" if image.url_transformed_qr else None,
            description=description,
            updated_at=datetime.utcnow(),
        )

        db.add(db_image)
        db.commit()

        # Create QR code for the transformed image URL
        qrcode_image = qrcode.make(transformed_image_url)
        qrcode_data = qrcode_image.to_bytes()

        return {
            "public_id": public_id,
            "transformed_image_url": transformed_image_url,
            "qrcode_data": qrcode_data,
        }

    except Exception as e:
        print(f"Error uploading to Cloudinary: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload image to Cloudinary")



# Assuming you have a function to get the image by ID from the database
def get_image_by_id(db: Session, image_id: str):
    return db.query(DBImage).filter(DBImage.id == image_id).first()
