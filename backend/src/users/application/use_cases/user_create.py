from src.users.domain.dtos import UserCreateDTO, UserReadDTO
from src.users.domain.entities import UserCreate
from src.users.domain.interfaces.user_uow import IUserUnitOfWork


async def create_user(user_data: UserCreateDTO, uow: IUserUnitOfWork) -> UserReadDTO:
    request = UserCreate(external_id=user_data.user_id, app_bundle=user_data.app_bundle, tokens=0)
    async with uow:
        user = await uow.users.create(request)
        await uow.commit()
    return UserReadDTO(user_id=user.external_id, app_bundle=user.app_bundle, tokens=user.tokens)
