from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from src.database.models import User
from src.database.db import get_db

import logging

logger = logging.getLogger(__name__)

security = HTTPBasic()

AUTH_LOGIN_URL = "/api/auth/login"


class Auth:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl=AUTH_LOGIN_URL)

    async def get_current_user(self, 
                               token: str = Depends(oauth2_scheme), 
                               db: Session = Depends(get_db)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            user = await user(db)
            # if user is None:
            #     raise credentials_exception
            return user

        except Exception as e:
            logger.error(f"Error: {e}")
            raise credentials_exception


auth_service = Auth(
    # schemes=["bcrypt"],
    # deprecated="auto",
    # secret_key="secret_key",
    # algorithm="HS256",
    # token_url=AUTH_LOGIN_URL
)    

# Викликайте асинхронний метод з екземпляру Auth
# user = await auth_service.get_current_user()



