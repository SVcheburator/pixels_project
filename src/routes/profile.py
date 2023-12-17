from fastapi import APIRouter, Depends, HTTPException, Path, status, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader
import hashlib 

from src.conf import messages
from src.database.db import get_db
from src.database.models import User, Role
from src.repository import profile as repository_profile
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import settings
from src.schemas import RequestUserName, UpdateProfile, UserDb, UserRole

router = APIRouter(prefix="/users/profile", tags=["users"])

# allowed_operations_roles = RoleAccess([Role.admin])


@router.get("/", status_code=status.HTTP_200_OK)
async def read_profile(
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get profile of current user

    :param current_user: The current user.
    :type current_user: User
    :return: The current user.
    :rtype: dict
    """
    reasult = await repository_profile.read_profile(current_user, db)
    return reasult



@router.patch("/", status_code=status.HTTP_200_OK)
async def update_profile(
    data: UpdateProfile,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get profile of current user

    :param current_user: The current user.
    :type current_user: User
    :return: The current user.
    :rtype: dict
    """
    updated = await repository_profile.update_profile(data, current_user, db)
    if updated:
        result = await repository_profile.read_profile(current_user, db)
        return result
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND
    )


@router.patch("/avatar", response_model=UserDb)
async def update_avatar(
    file: UploadFile = File(),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Updates user's avatar.

    :param file: The image file of the avatar.
    :type file: UploadFile
    :param current_user: The current user.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: The User with a new avatar.
    :rtype: UserDb
    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )
    app_name = "PixelApp"
    user_hash = hashlib.sha224("current_user.email".encode()).hexdigest()
    r = cloudinary.uploader.upload(
        file.file, public_id=f"{app_name}/{user_hash}", overwrite=True
    )
    src_url = cloudinary.CloudinaryImage(
        f"{app_name}/{user_hash}"
    ).build_url(width=250, height=250, crop="fill", version=r.get("version"))
    user = await repository_users.update_avatar(current_user.email, src_url, db)  # type: ignore
    return user


@router.get("/{username}", status_code=status.HTTP_200_OK)
async def read_profile_user(
    username: str = Path(min_length=5, max_length=16),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get profile of selected user by their username

    :param username: username of user.
    :type current_user: str
    :return: The current user.
    :rtype: dict
    """
    user = await repository_users.get_user_by_username(username, db)
    result = await repository_profile.read_profile(user, db)

    return result
