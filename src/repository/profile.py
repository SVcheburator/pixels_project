from libgravatar import Gravatar
from sqlalchemy import func
from sqlalchemy.orm import Session
from repository.users import clear_user_cache, get_user_by_username

from src.database.models import User, Role, Comment, Image
from src.schemas import UpdateProfile, UserModel
from src.services.auth import auth_service


async def read_profile(user: User, db: Session) -> dict:
    """
    Retrieves a user profile.

    :param email: An email to get user from the database by.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: The user.
    :rtype: User
    """
    result = {}
    if user:
        # comments_count = db.query(Comment).filter(Comment.owner_id == user.id).count()
        comments_count = db.query(func.count(Comment.owner_id  == user.id)).scalar()
        images_count = db.query(func.count(Image.owner_id  == user.id)).scalar()
        result = {
        "username": user.username,
        "email": user.email,
        "avatar": user.avatar,
        "created_at": user.created_at,
        "comments_count": comments_count,
        "images_count": images_count
    }
    return result


async def update_profile(data: UpdateProfile, user: User, db: Session) -> bool| None:
    """
    Retrieves a user profile.

    :param email: An email to get user from the database by.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: The user.
    :rtype: User
    """
    if user:
        if data.username:
            newuser: User = await get_user_by_username(str(data.username), db)
            if not newuser:
                user.username = str(data.username)
                db.commit()
                clear_user_cache(user)
                return True




