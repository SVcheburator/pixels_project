from fastapi import APIRouter, Depends, File, Form, HTTPException, Path, UploadFile, status
from sqlalchemy.orm import Session

from src.conf import messages
from src.database.db import get_db
from src.database.models import User, Role
from src.repository import users as repository_users
from src.repository import profile as repository_profile
from src.services.auth import auth_service
from src.schemas import UpdateFullProfile, UpdateProfile, UserDb
from src.services.roles import RoleAccess
from src.services import cloudinary_image as cloudinary_service


router = APIRouter(prefix="/users", tags=["users"])

allowed_operations_modify = RoleAccess([Role.admin])
allowed_operations_bans = RoleAccess([Role.admin])
allowed_operations_delete = RoleAccess([Role.admin])
allowed_operations_admin = RoleAccess([Role.admin])


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


# @router.get(
#     "/ban/{user_id}",
#     dependencies=[Depends(allowed_operations_bans)],
#     status_code=status.HTTP_200_OK,
#     response_description=messages.USER_ACCEPTED,
#     name="Ban user",
# )
# async def ban_user(
#     user_id: int,
#     owner: User = Depends(auth_service.get_current_user),
#     db: Session = Depends(get_db),
# ):
#     """Ban user by their ID, does not allow users to log in.  Allowed for roles: admin.

#     :param user_id: id of user
#     :type user_id: int
#     :param owner: _description_, defaults to Depends(auth_service.get_current_user)
#     :type owner: User, optional
#     :param db: _description_, defaults to Depends(get_db)
#     :type db: Session, optional
#     """

#     # if str(owner.role) != "Role.admin":
#     #     print(f"{str(owner.role)=}")
#     #     raise HTTPException(
#     #         status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.USER_INVALID_ROLE
#     #     )
#     if owner.id == user_id:  # type: ignore
#         raise HTTPException(
#             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#             detail=messages.USER_CANT_OPERATE_HIMSELF,
#         )
#     user = await repository_users.update_active(user_id, active=False, db=db)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND
#         )
#     return {"detail": messages.USER_ACCEPTED}


# @router.get(
#     "/unban/{user_id}",
#     dependencies=[Depends(allowed_operations_bans)],
#     status_code=status.HTTP_200_OK,
#     response_description=messages.USER_ACCEPTED,
#     name="UnBan user",
# )
# async def unban_user(
#     user_id: int,
#     owner: User = Depends(auth_service.get_current_user),
#     db: Session = Depends(get_db),
# ):
#     """Unban user by their ID, allow users to log in.  Allowed for roles: admin.

#     :param user_id: id of user
#     :type user_id: int
#     :param owner: _description_, defaults to Depends(auth_service.get_current_user)
#     :type owner: User, optional
#     :param db: _description_, defaults to Depends(get_db)
#     :type db: Session, optional
#     """
#     # if str(owner.role) != "Role.admin":
#     #     raise HTTPException(
#     #         status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.USER_INVALID_ROLE
#     #     )
#     if owner.id == user_id:  # type: ignore
#         raise HTTPException(
#             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#             detail=messages.USER_CANT_OPERATE_HIMSELF,
#         )
#     user = await repository_users.update_active(user_id, active=True, db=db)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND
#         )
#     return {"detail": messages.USER_ACCEPTED}


# @router.patch(
#     "/role/{user_id}",
#     dependencies=[Depends(allowed_operations_modify)],
#     status_code=status.HTTP_200_OK,
#     response_description=messages.USER_ACCEPTED,
#     name="Change role of user",
# )
# async def update_role_user(
#     user_id: int,
#     user_role: UserRole,
#     owner: User = Depends(auth_service.get_current_user),
#     db: Session = Depends(get_db),
# ):
#     """Unban user by their ID, allow users to log in..

#     :param user_id: id of user
#     :type user_id: int
#     :param owner: _description_, defaults to Depends(auth_service.get_current_user)
#     :type owner: User, optional
#     :param db: _description_, defaults to Depends(get_db)
#     :type db: Session, optional
#     """
#     # if str(owner.role) != "Role.admin":
#     #     raise HTTPException(
#     #         status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.USER_INVALID_ROLE
#     #     )
#     if owner.id == user_id:  # type: ignore
#         raise HTTPException(
#             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#             detail=messages.USER_CANT_OPERATE_HIMSELF,
#         )
#     user = await repository_users.update_role_user(user_id, role=user_role.role, db=db)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND
#         )
#     return {"detail": messages.USER_ACCEPTED}


@router.patch(
    "/{user_id}",
    dependencies=[Depends(allowed_operations_modify)],
    status_code=status.HTTP_200_OK,
    response_description=messages.USER_ACCEPTED,
    name="Change user's data",
)
async def update_user(
    data: UpdateFullProfile,
    user_id: int = Path(gt=0),
    owner: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """Update user data by their ID, Allowed only for Admin.

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
    data_dict = data.model_dump()
    if repository_users.dict_not_empty(data_dict):
        user = await repository_users.update_user(user_id, data=data_dict, db=db)
        if user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND
            )
        return {"detail": messages.USER_ACCEPTED}
    raise HTTPException(
        status_code=status.HTTP_304_NOT_MODIFIED, detail=messages.USER_NOT_CHANGED
    )


@router.patch(
    "/me/",
    status_code=status.HTTP_200_OK,
    response_description=messages.USER_ACCEPTED,
    name="Change user's data",
)
async def update_user_me(
    data: UpdateProfile,
    owner: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user data .

    :param user_id: id of user
    :type user_id: int
    :param owner: _description_, defaults to Depends(auth_service.get_current_user)
    :type owner: User, optional
    :param db: _description_, defaults to Depends(get_db)
    :type db: Session, optional
    """
    data_dict = data.model_dump()
    if repository_users.dict_not_empty(data_dict):
        data_dict["role"] = None
        data_dict["is_active"] = None
        user = await repository_users.update_user(owner.id, data=data_dict, db=db) # type: ignore
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND
            )
        return {"detail": messages.USER_ACCEPTED}
    raise HTTPException(
        status_code=status.HTTP_304_NOT_MODIFIED, detail=messages.USER_NOT_CHANGED
    )


@router.delete(
    "/{user_id}",
    dependencies=[Depends(allowed_operations_delete)],
    status_code=status.HTTP_200_OK,
    response_description=messages.USER_ACCEPTED,
    name="Delete user",
)
async def delete_user(
    user_id: int = Path(gt=0),
    owner: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """Delete user by their ID, with not active state.  Allowed for roles: admin.

    :param user_id: id of user
    :type user_id: int
    :param owner: _description_, defaults to Depends(auth_service.get_current_user)
    :type owner: User, optional
    :param db: _description_, defaults to Depends(get_db)
    :type db: Session, optional
    """
    if owner.id == user_id:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=messages.USER_CANT_OPERATE_HIMSELF,
        )
    user = await repository_users.delete_user(user_id, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND
        )
    return {"detail": messages.USER_ACCEPTED}


@router.patch(
    "/{user_id}/avatar",
    response_model=UserDb,
    dependencies=[Depends(allowed_operations_modify)],
)
async def update_avatar(
    user_id: int = Path(gt=0),
    file: UploadFile = File(description="Upload image file for user's avatar"),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Updates user's avatar by their id. Allowed only for Admin.

    :param file: The image file of the avatar.
    :type file: UploadFile
    :param current_user: The current user.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: The User with a new avatar.
    :rtype: UserDb
    """
    target_user = await repository_users.get_user_by_id(id=user_id, db=db, active=None)
    if target_user:
        src_url = cloudinary_service.build_avatar_cloudinary_url(
            file, str(target_user.email)
        )
        user = await repository_users.update_avatar(target_user.email, src_url, db)  # type: ignore
        return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND
    )


@router.patch("/avatar", response_model=UserDb)
async def update_avatar_me(
    file: UploadFile = File(description="Upload image file for your avatar"),
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
    src_url = cloudinary_service.build_avatar_cloudinary_url(
        file, str(current_user.email)
    )
    user = await repository_users.update_avatar(current_user.email, src_url, db)  # type: ignore
    return user


@router.get("/profile", status_code=status.HTTP_200_OK)
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
    result = await repository_profile.read_profile(current_user, db)
    return result


@router.patch("/profile", status_code=status.HTTP_200_OK)
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



@router.get("/{username}/profile", status_code=status.HTTP_200_OK)
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
    if user:
        result = await repository_profile.read_profile(user, db)
        return result
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND
    )


