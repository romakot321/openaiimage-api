from fastapi import APIRouter
from src.users.domain.dtos import UserCreateDTO, UserReadDTO
from src.users.presentation.dependencies import UserUoWDepend
from src.users.application.use_cases.user_create import create_user as uc_create_user


router = APIRouter()


@router.post("", response_model=UserReadDTO)
async def create_user(user_data: UserCreateDTO, uow: UserUoWDepend):
    return await uc_create_user(user_data, uow)

