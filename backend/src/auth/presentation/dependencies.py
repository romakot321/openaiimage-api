from typing import Annotated
from fastapi import Depends
from src.auth.application.service import AuthService
from src.users.domain.entities import User


AuthServiceDepend = Annotated[AuthService, Depends()]
CurrentUserDepend = Annotated[User, Depends(AuthService.get_current_user)]
