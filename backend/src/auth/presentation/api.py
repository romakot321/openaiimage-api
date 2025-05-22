from fastapi import APIRouter, Depends
from src.auth.application.service import AuthService
from src.auth.domain.dtos import AuthLoginDTO, AuthTokenDTO
from src.auth.presentation.dependencies import AuthServiceDepend, CurrentUserDepend
from src.users.domain.dtos import UserReadDTO

router = APIRouter()


@router.post("/login", response_model=AuthTokenDTO)
async def login(login_data: AuthLoginDTO, auth_service: AuthServiceDepend):
    token = await auth_service.login(login_data)
    return AuthTokenDTO(api_token=token)


@router.get("/me", response_model=UserReadDTO)
async def get_me(user: CurrentUserDepend):
    return UserReadDTO(user_id=user.external_id, app_bundle=user.app_bundle, tokens=user.tokens)
