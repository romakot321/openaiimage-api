from fastapi import APIRouter, Header, Request
from src.users.application.apphud_worker import AppHudWorker
from src.users.domain.dtos import UserCreateDTO, UserReadDTO
from src.users.presentation.dependencies import UserUoWDepend
from src.users.application.use_cases.user_create import create_user as uc_create_user


router = APIRouter()


@router.post("", response_model=UserReadDTO)
async def create_user(user_data: UserCreateDTO, uow: UserUoWDepend):
    return await uc_create_user(user_data, uow)


@router.post("/apphud", status_code=202)
async def apphud_webhook(request: Request, uow: UserUoWDepend, x_apphud_token: str = Header()):
    raw_body = await request.json()
    await AppHudWorker(uow, x_apphud_token).process_webhook(raw_body)
