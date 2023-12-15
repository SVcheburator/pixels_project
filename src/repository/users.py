from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User, Role
from src.schemas import UserModel
from src.services.auth import auth_service


def clear_user_cache(user: User) -> None:
    """_summary_

    :param user: Clear user from cached storage
    :type user: User
    """
    auth_service.r.delete(f"user:{user.email}")


async def get_user_by_email(email: str, db: Session) -> User:
    """
    Retrieves a user by his email.

    :param email: An email to get user from the database by.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: The user.
    :rtype: User
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    Creates a new user.

    :param body: The data for the user to create.
    :type body: UserModel
    :param db: The database session.
    :type db: Session
    :return: The newly created user.
    :rtype: User
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Creates an update token.

    :param user: The user to create an update token for.
    :type user: User
    :param token: The token.
    :type token: str | None
    :param db: The database session.
    :type db: Session
    :return: None.
    :rtype: None
    """
    if user:
        user.refresh_token = token  # type: ignore
        db.commit()
        clear_user_cache(user)


async def confirmed_email(email: str, db: Session) -> None:
    """
    Updates email confirmation status.

    :param email: The email.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: None.
    :rtype: None
    """
    user = await get_user_by_email(email, db)
    if user:
        user.confirmed = True  # type: ignore
        user.active = True  # type: ignore
        db.commit()


async def update_avatar(email: str, url: str, db: Session) -> User:
    """
    Updates user's avatar.

    :param email: The email.
    :type email: str
    :param url: The url of the avatar.
    :type url: str
    :param db: The database session.
    :type db: Session
    :return: The User with a new avatar.
    :rtype: User
    """
    user = await get_user_by_email(email, db)
    if user:
        user.avatar = url  # type: ignore
        db.commit()
        clear_user_cache(user)
    return user


async def get_user_by_id(id: int, db: Session) -> User:
    """
    Retrieves a user by his id.

    :param id: An id to get user from the database by.
    :type id: int
    :param db: The database session.
    :type db: Session
    :return: The user.
    :rtype: User
    """
    return db.query(User).filter(User.id == id).first()


async def update_active(user_id: int, active: bool, db: Session) -> User:
    """
    Updates user's active state.

    :param user_id: The email.
    :type user_id: int
    :param active: The active state of user.
    :type active: bool
    :param db: The database session.
    :type db: Session
    :return: The user.
    :rtype: User
    """
    user = await get_user_by_id(user_id, db)
    if user:
        user.active = active  # type: ignore
        db.commit()
        clear_user_cache(user)
    return user
