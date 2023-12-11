from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User, Role
from src.schemas import UserModel


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
    new_user = User(**body.dict(), avatar=avatar)
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
    user.refresh_token = token
    db.commit()


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
    user.confirmed = True
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
    user.avatar = url
    db.commit()
    return user