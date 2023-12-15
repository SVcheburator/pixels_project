from typing import Any, List

from fastapi import Depends, HTTPException, status, Request

from src.database.models import User, Role
from src.services.auth import auth_service
from src.conf import messages


class RoleAccess:
    def __init__(self, allowed_roles: List[Role]) -> None:
        """
        The __init__ function is called when the class is instantiated.
            It sets up the instance of the class with a list of allowed roles.
        
        :param self: Represent the instance of the class
        :param allowed_roles: List[Role]: Define the allowed roles for a command
        :return: None
        """
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        request: Request,
        current_user: User = Depends(auth_service.get_current_user),
    ) -> Any:
        """
        The __call__ function is the actual decorator (async functor).
        It takes in a function, adds some code before and after it runs, then returns all of that as a function.
        
        
        :param self: Access the class attributes
        :param request: Request: Get the request method and url
        :param current_user: User: Get the current user from the database
        :param : Get the current user from the database
        :return: The decorated function
        """
        print(request.method, request.url)
        print(f"User role {current_user.role}")
        print(f"Allowed roles: {self.allowed_roles}")
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=messages.OPERATION_FORBIDDEN,
            )
