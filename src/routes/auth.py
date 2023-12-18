from typing import List

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Security,
    BackgroundTasks,
    Request,
)
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from src.conf import messages
from src.database.db import get_db
from src.database.models import Role
from src.schemas import (
    UserModel,
    UserResponse,
    TokenModel,
    RequestEmail,
    UserModelCaptcha,
)
from src.repository import users as repository_users
from src.repository import logout as repository_logout
from src.services import hcaptcha as hcaptcha_service
from src.services.auth import auth_service
from src.services.emails import send_email

router = APIRouter(prefix="/auth", tags=["Authorization"])
security = HTTPBearer()


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    body: UserModel,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Signups user.

    :param body: The data for the user to sign up.
    :type body: UserModel
    :param background_tasks: Background tasks.
    :type background_tasks: BackgroundTasks
    :param request: The request.
    :type request: Request
    :param db: The database session.
    :type db: Session
    :return: The UserResponse model with the new user and information about successfull user creation.
    :rtype: dict
    """
    exist_user = await repository_users.get_user_by_email(body.email, db, active=None)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=messages.AUTH_ALREADY_EXIST
        )
    exist_user = await repository_users.get_user_by_username(body.username, db, active=None)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=messages.AUTH_ALREADY_EXIST
        )
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    if new_user:
        background_tasks.add_task(
            send_email, new_user.email, new_user.username, request.base_url
        )
        return {
            "user": new_user,
            "role": Role.user,
            "detail": messages.AUTH_USER_CREATED_CONFIRM
        }
    print("SOME PROBLEM")
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT, detail=messages.AUTH_ALREADY_EXIST
    )

@router.post("/login", response_model=TokenModel)
async def login(
    body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Logins user.

    :param body: The data for the user to sign up.
    :type body: OAuth2PasswordRequestForm
    :param db: The database session.
    :type db: Session
    :return: The TokenModel model with the access token and refresh token.
    :rtype: dict
    """
    user = await repository_users.get_user_by_email(body.username, db, active=None)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.AUTH_EMAIL_INVALID
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.AUTH_EMAIL_NOT_CONF
        )
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.AUTH_EMAIL_NOT_ACTIVE
        )
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.AUTH_INVALID_PASSW
        )
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/refresh_token", response_model=TokenModel)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
):
    """
    Refreshes token.

    :param credentials: Credentials.
    :type credentials: HTTPAuthorizationCredentials
    :param db: The database session.
    :type db: Session
    :return: The TokenModel model with the access token and refresh token.
    :rtype: dict
    """
    token = credentials.credentials
    token_banned_is = await repository_logout.check_token(token, db)
    if token_banned_is:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.AUTH_INVALID_AUTH_TOKEN
        )
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user and user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.AUTH_INVALID_REF_TOKEN
        )

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Confirms user's email.

    :param token: Token.
    :type token: str
    :param db: The database session.
    :type db: Session
    :return: The message about email confirmation.
    :rtype: dict
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db, active=None)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=messages.AUTH_VERIFY_ERROR
        )
    if user.confirmed:
        return {"message": messages.AUTH_EMAIL_ALREADY_CONF}
    if await repository_users.confirmed_email(email, db):
        return {"message": messages.AUTH_EMAIL_CONF}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail=messages.AUTH_VERIFY_ERROR
    )


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Requests email.

    :param body: Email.
    :type body: RequestEmail
    :param background_tasks: Background tasks.
    :type background_tasks: BackgroundTasks
    :param request: The request.
    :type request: Request
    :param db: The database session.
    :type db: Session
    :return: The message about email request.
    :rtype: dict
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": messages.AUTH_EMAIL_ALREADY_CONF}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": messages.AUTH_EMAIL_CHECK_CONF}


@router.get("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
):
    """
    logout and add token token to banlist.

    :param credentials: Credentials.
    :type credentials: HTTPAuthorizationCredentials
    :param db: The database session.
    :type db: Session
    :return: empty content. 204 status code.
    :rtype: dict
    """
    token = credentials.credentials
    token_banned_is = await repository_logout.check_token(token, db)
    if token_banned_is:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.AUTH_INVALID_TOKEN
        )
    await repository_logout.add_token(token, db)
    return {}


@router.post(
    "/signup/cap", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup_cap(
    body: UserModelCaptcha,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Signups user with Captha.

    :param body: The data for the user to sign up.
    :type body: UserModelCaptcha
    :param background_tasks: Background tasks.
    :type background_tasks: BackgroundTasks
    :param request: The request.
    :type request: Request
    :param db: The database session.
    :type db: Session
    :return: The UserResponse model with the new user and information about successfull user creation.
    :rtype: dict
    """
    captcha_ok = await hcaptcha_service.verify(body.h_captcha_response)
    if not captcha_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.AUTH_INVALID_CAPTCHA
        )
    del body.h_captcha_response
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=messages.AUTH_ALREADY_EXIST
        )
    try:
        body.password = auth_service.get_password_hash(body.password)
        new_user = await repository_users.create_user(body, db)
        background_tasks.add_task(
            send_email, new_user.email, new_user.username, request.base_url
        )
        return {
            "user": new_user,
            "role": Role.user,
            "detail": messages.AUTH_USER_CREATED_CONFIRM,
        }
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=messages.AUTH_TROUBLES.format(err)
        )
