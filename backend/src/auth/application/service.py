from uuid import UUID
import jwt
from fastapi import HTTPException, Header
from src.auth.domain.dtos import AuthLoginDTO
from src.users.domain.entities import User
from src.users.domain.interfaces.user_uow import IUserUnitOfWork
from src.users.presentation.dependencies import UserUoWDepend
from src.core.config import settings


class AuthService:
    def __init__(self, user_uow: UserUoWDepend) -> None:
        self.user_uow: IUserUnitOfWork = user_uow
        self.unauthorized_exception = HTTPException(401, detail='Invalid Api-Token')

    @classmethod
    def _generate_token(cls, user_id: UUID) -> str:
        token = jwt.encode(
            payload={"sub": str(user_id)}, key=settings.SECRET_KEY, algorithm="HS256"
        )
        return token

    @classmethod
    def _decode_token(cls, token: str) -> dict[str, str] | None:
        try:
            payload = jwt.decode(
                jwt=token, key=settings.SECRET_KEY, algorithms=["HS256"]
            )
        except jwt.exceptions.InvalidTokenError:
            return None

        return payload

    async def _validate_api_token(self, token: str) -> User:
        token_payload = self._decode_token(token)
        if token_payload is None:
            raise self.unauthorized_exception
        if token_payload.get("sub") is None:
            raise self.unauthorized_exception

        async with self.user_uow:
            try:
                user = await self.user_uow.users.get_by_pk(UUID(token_payload["sub"]))
            except HTTPException as e:
                if e.status_code == 404:
                    raise self.unauthorized_exception
                raise e
        return user

    async def login(self, login_data: AuthLoginDTO) -> str:
        async with self.user_uow:
            try:
                user = await self.user_uow.users.get_by_external(login_data.user_id, login_data.app_bundle)
            except HTTPException as e:
                if e.status_code == 404:
                    raise self.unauthorized_exception
                raise e
        return self._generate_token(user.id)

    @classmethod
    async def get_current_user(
        cls, user_uow: UserUoWDepend, api_token: str = Header()
    ) -> User:
        self = cls(user_uow)
        return await self._validate_api_token(api_token)
