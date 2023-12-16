from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.conf import messages
from src.database.db import get_db
from src.database.models import User, Role
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import settings
from src.schemas import UserDb, UserRole
from src.services.roles import RoleAccess

router = APIRouter(prefix="/users", tags=["users"])

allowed_operations_roles = RoleAccess([Role.admin])
allowed_operations_bans = RoleAccess([Role.admin])

@router.get("/me/", response_model=UserDb)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    Gets a current user.

    :param current_user: The current user.
    :type current_user: User
    :return: The current user.
    :rtype: UserDb
    """
    return current_user


@router.patch("/avatar", response_model=UserDb)
async def update_avatar_user(
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

    r = cloudinary.uploader.upload(
        file.file, public_id=f"ContactsApp/{current_user.username}", overwrite=True
    )
    src_url = cloudinary.CloudinaryImage(
        f"ContactsApp/{current_user.username}"
    ).build_url(width=250, height=250, crop="fill", version=r.get("version"))
    user = await repository_users.update_avatar(current_user.email, src_url, db)  # type: ignore
    return user


@router.get(
    "/ban/{user_id}",
    dependencies=[Depends(allowed_operations_bans)],
    status_code=status.HTTP_200_OK,
    response_description=messages.USER_ACCEPDED,
    name="Ban user by id, allowed admin only",
)
async def ban_user(
    user_id: int,
    owner: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """Ban user by their ID, does not allow users to log in.  Allowed for roles: admin.

    :param user_id: id of user
    :type user_id: int
    :param owner: _description_, defaults to Depends(auth_service.get_current_user)
    :type owner: User, optional
    :param db: _description_, defaults to Depends(get_db)
    :type db: Session, optional
    """

    # if str(owner.role) != "Role.admin":
    #     print(f"{str(owner.role)=}")
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.USER_INVALID_ROLE
    #     )
    if owner.id == user_id:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=messages.USER_CANT_OPERATE_HIMSELF,
        )
    user = await repository_users.update_active(user_id, active=False, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND
        )
    return {"detail": messages.USER_ACCEPDED}


@router.get(
    "/unban/{user_id}",
    dependencies=[Depends(allowed_operations_bans)],
    status_code=status.HTTP_200_OK,
    response_description=messages.USER_ACCEPDED,
    name="UnBan user by id, allowed admin only",
)
async def unban_user(
    user_id: int,
    owner: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """Unban user by their ID, allow users to log in.  Allowed for roles: admin.

    :param user_id: id of user
    :type user_id: int
    :param owner: _description_, defaults to Depends(auth_service.get_current_user)
    :type owner: User, optional
    :param db: _description_, defaults to Depends(get_db)
    :type db: Session, optional
    """
    # if str(owner.role) != "Role.admin":
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.USER_INVALID_ROLE
    #     )
    if owner.id == user_id:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=messages.USER_CANT_OPERATE_HIMSELF,
        )
    user = await repository_users.update_active(user_id, active=True, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND
        )
    return {"detail": messages.USER_ACCEPDED}


@router.patch(
    "/role/{user_id}",
    dependencies=[Depends(allowed_operations_roles)],
    status_code=status.HTTP_200_OK,
    response_description=messages.USER_ACCEPDED,
    name="Change role user by id, allowed admin only",
)
async def update_role_user(
    user_id: int,
    user_role: UserRole,
    owner: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """Unban user by their ID, allow users to log in.  Allowed for roles: admin.

    :param user_id: id of user
    :type user_id: int
    :param owner: _description_, defaults to Depends(auth_service.get_current_user)
    :type owner: User, optional
    :param db: _description_, defaults to Depends(get_db)
    :type db: Session, optional
    """
    # if str(owner.role) != "Role.admin":
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.USER_INVALID_ROLE
    #     )
    if owner.id == user_id:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=messages.USER_CANT_OPERATE_HIMSELF,
        )
    user = await repository_users.update_role_user(user_id, role=user_role.role, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND
        )
    return {"detail": messages.USER_ACCEPDED}
