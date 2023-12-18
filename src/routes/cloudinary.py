from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import Image
from src.services.cloudinary import cloudinary 
import cloudinary
from cloudinary.uploader import upload
import cloudinary.api



from fastapi import APIRouter, Depends
from src.conf.config import settings

class CloudinaryService:
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )

cloud_router = APIRouter(prefix='/cloudinary')


@cloud_router.get("/transformed_image/{image_id}")
def transform_and_update_image(image_id: str, angle: int = 45, db: Session = Depends(get_db)):
    image = db.query(Image).filter(Image.url_original.contains(image_id)).first()

    if image:
        url_original = image.url_original
        public_id = '/'.join(url_original.split('/')[7:])
        
        transformation = {"angle": angle}

        # Завантажити трансформоване зображення на Cloudinary
        response = upload(url_original, transformation=transformation, public_id=public_id)

        transformed_image_url = response['secure_url']

        db.query(Image).filter(Image.url_original.contains(image_id)).update({"url_transformed": transformed_image_url})
        db.commit()

        print("1:", image_id)
        # print("2:", Image.id)
        print("Original Image URL:", url_original)
        print("Transformed Image URL:", transformed_image_url)

        return {"message": f"Image transformed and updated successfully. Rotated by {angle} degrees.", "transformed_image_url": transformed_image_url}

    return {"error": "Image not found."}