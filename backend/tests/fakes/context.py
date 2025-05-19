from uuid import UUID, uuid4
from fastapi import HTTPException
from src.contexts.domain.dtos import ContextUsageDTO
from src.contexts.domain.entities import (
    Context,
    ContextCreate,
    ContextEntity,
    ContextEntityCreate,
)
from src.contexts.domain.interfaces.context_entity_repository import (
    IContextEntityRepository,
)
from src.contexts.domain.interfaces.context_repository import IContextRepository
from src.contexts.domain.interfaces.context_uow import IContextUnitOfWork


class FakeContextEntityRepository(IContextEntityRepository):
    def __init__(self):
        self._entities: list[ContextEntity] = []
        self._last_context_id = 0

    async def create(self, task: ContextEntityCreate) -> ContextEntity:
        user = ContextEntity(**task.model_dump())
        self._entities.append(user)
        return user

    async def get_list_by_context_id(self, context_id: UUID) -> list[ContextEntity]:
        ret = []
        for entity in self._entities:
            if entity.context_id == context_id:
                ret.append(entity)
        return ret

    async def get_context_usage(self, context_id: UUID) -> ContextUsageDTO:
        return ContextUsageDTO(text_used=0, images_used=0)

    async def delete_by_pk(self, pk: UUID) -> None:
        for entity in self._entities:
            if entity.id == pk:
                self._entities.remove(entity)
                return

    def _get_new_context_id(self) -> UUID:
        return uuid4()


class FakeContextRepository(IContextRepository):
    def __init__(self, entity_repository: FakeContextEntityRepository):
        self._entity_repository = entity_repository
        self._contexts: list[Context] = []
        self._last_context_id = 0

    async def create(self, task: ContextCreate) -> Context:
        user = Context(
            id=self._get_new_context_id(), entities=[], tasks=[], **task.model_dump()
        )
        self._contexts.append(user)
        return user

    async def get_by_pk(self, pk: UUID) -> Context:
        for context in self._contexts:
            if context.id == pk:
                return Context(
                    **context.model_dump(exclude="entities"),
                    entities=await self._entity_repository.get_list_by_context_id(pk),
                )

        raise HTTPException(404)

    async def delete_by_pk(self, pk: UUID) -> None:
        context = await self.get_by_pk(pk)
        self._contexts.remove(context)

    async def get_user_last(self, user_id: str) -> Context:
        for context in self._contexts[::-1]:
            if context.user_id == user_id:
                return Context(
                    **context.model_dump(exclude="entities"),
                    entities=await self._entity_repository.get_list_by_context_id(
                        context.id
                    ),
                )
        raise HTTPException(404)

    def _get_new_context_id(self) -> UUID:
        return uuid4()


class FakeContextUnitOfWork(IContextUnitOfWork):
    contexts: IContextRepository
    context_entity: IContextEntityRepository

    def __init__(self):
        self.context_entity = FakeContextEntityRepository()
        self.contexts = FakeContextRepository(self.context_entity)
        self.committed = False

    async def _commit(self):
        self.committed = True

    async def _rollback(self):
        pass
