from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User, Role
from src.schemas import UserModel
from src.services.auth import auth_service


def dict_is_empty(data: dict) -> bool:
    return all(v is None for v in data.values())


def dict_not_empty(data: dict) -> bool:
    return any(v is not None for v in data.values())


def clear_user_cache(user: User) -> None:
    """_summary_

    :param user: Clear user from cached storage
    :type user: User
    """
    auth_service.r.delete(f"user:{user.email}")


async def is_present_admin(db: Session) -> bool:
    """search if is present admin in users
    :param db: The database session.
    :type db: Session
    :return: True if any admin is
    :rtype: bool
    """
    result = db.query(User).filter(User.role == Role.admin).first()
    return result is not None


async def get_user_by_email(
    email: str, db: Session, active: bool | None = True
) -> User:
    """
    Retrieves a user by his email.

    :param email: An email to get user from the database by.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: The user.
    :rtype: User
    """
    query = db.query(User).filter(User.email == email)
    if active is not None:
        query = query.filter(User.active == active)
    return query.first()


async def get_user_by_username(
    username: str, db: Session, active: bool | None = True
) -> User:
    """
    Retrieves a user by his username.

    :param username: An username to get user from the database by.
    :type username: str
    :param db: The database session.
    :type db: Session
    :return: The user.
    :rtype: User
    """
    query = db.query(User).filter(User.username == username)
    if active is not None:
        query = query.filter(User.active == active)
    return query.first()


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
    # Search any admin if not present assign thios user as admin
    if not await is_present_admin(db):
        new_user.role = Role.admin
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as err:
        print(f"ERROR create_user {err}")


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


async def confirmed_email(email: str, db: Session) -> bool | None:
    """
    Updates email confirmation status.

    :param email: The email.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: None.
    :rtype: None
    """
    user = await get_user_by_email(email, db, active=False)
    if user:
        user.confirmed = True  # type: ignore
        user.active = True  # type: ignore
        db.commit()
        return True


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


async def get_user_by_id(id: int, db: Session, active: bool | None = True) -> User:
    """
    Retrieves a user by his id.

    :param id: An id to get user from the database by.
    :type id: int
    :param db: The database session.
    :type db: Session
    :return: The user.
    :rtype: User
    """
    query = db.query(User).filter(
        User.id == id,
    )
    if active is not None:
        query = query.filter(User.active == active)
    return query.first()


async def update_active(user_id: int, active: bool, db: Session) -> User:
    """
    Updates user's active state.

    :param user_id:  id of user.
    :type user_id: int
    :param active: The active state of user.
    :type active: bool
    :param db: The database session.
    :type db: Session
    :return: The user.
    :rtype: User
    """
    user = await get_user_by_id(user_id, active=not active, db=db)
    if user:
        user.active = active  # type: ignore
        db.commit()
        clear_user_cache(user)
    return user


async def update_role_user(user_id: int, role: Role, db: Session) -> User:
    """
    Updates user's role.

    :param user_id: id of user.
    :type user_id: int
    :param active: role of user.
    :type active: str
    :param db: The database session.
    :type db: Session
    :return: The user.
    :rtype: User
    """
    user = await get_user_by_id(user_id, db)
    if user:
        user.role = role  # type: ignore
        db.commit()
        clear_user_cache(user)
    return user


async def update_user(user_id: int, data: dict, db: Session) -> User | None:
    """
    Updates user's role.

    :param user_id: id of user.
    :type user_id: int
    :param active: role of user.
    :type active: str
    :param db: The database session.
    :type db: Session
    :return: The user.
    :rtype: User
    """
    user = await get_user_by_id(user_id, db, active=None)
    if user:
        if data.get("username") is not None:
            newuser: User = await get_user_by_username(
                str(data.get("username")), db, active=None
            )
            if newuser:
                return None
            user.username = data.get("username")  # type: ignore
        if data.get("is_active") is not None:
            user.active = data.get("is_active")  # type: ignore
        if data.get("role") is not None:
            user.role = data.get("role")  # type: ignore
        db.commit()
        clear_user_cache(user)
    return user


async def delete_user(user_id: int, db: Session) -> User:
    """
    Delete user's with not active state.

    :param user_id:  id of user.
    :type user_id: int
    :param db: The database session.
    :type db: Session
    :return: The user.
    :rtype: User
    """
    user = await get_user_by_id(user_id, active=False, db=db)
    if user:
        db.delete(user)
        db.commit()
        clear_user_cache(user)
    return user
