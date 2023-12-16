from fastapi import APIRouter, Depends, HTTPException, Path, status, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.conf import messages
from src.database.db import get_db
from src.database.models import User, Role
from src.repository import profile as repository_profile
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import settings
from src.schemas import RequestUserName, UserDb, UserRole

router = APIRouter(prefix="/users/profile", tags=["users"])

# allowed_operations_roles = RoleAccess([Role.admin])


@router.get("/me", status_code=status.HTTP_200_OK)
async def read_profile_me(
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get profile of curerent user

    :param current_user: The current user.
    :type current_user: User
    :return: The current user.
    :rtype: dict
    """
    reasult = await repository_profile.read_profile(current_user, db)
    return reasult

@router.get("/{username}", status_code=status.HTTP_200_OK)
async def read_profile(
    username: str = Path(min_length=5, max_length=16),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get profile of seected user by their username

    :param username: username of user.
    :type current_user: str
    :return: The current user.
    :rtype: dict
    """
    user = await repository_users.get_user_by_username(username, db)
    result = await repository_profile.read_profile(user, db)

    return result