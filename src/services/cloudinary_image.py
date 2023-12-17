import hashlib 

import cloudinary
import cloudinary.uploader

from fastapi import UploadFile

from src.conf.config import settings



cloudinary.config(
    cloud_name=settings.cloudinary_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True,
)

app_name = "PixelApp"

def build_avatar_cloudinary_url(file: UploadFile , email:str) -> str:
    user_hash = hashlib.sha224(email.encode()).hexdigest()
    r = cloudinary.uploader.upload(
        file.file, public_id=f"{app_name}/{user_hash}", overwrite=True
    )
    src_url = cloudinary.CloudinaryImage(
        f"{app_name}/{user_hash}"
    ).build_url(width=250, height=250, crop="fill", version=r.get("version"))
    return src_url