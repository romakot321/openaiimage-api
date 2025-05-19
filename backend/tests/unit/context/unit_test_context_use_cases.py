from uuid import uuid4
from fastapi import HTTPException
import pytest
from src.contexts.application.use_cases.context_create import create_context
from src.contexts.application.use_cases.context_delete import delete_context
from src.contexts.application.use_cases.context_get import get_context
from src.contexts.domain.dtos import ContextCreateDTO, ContextReadDTO
from src.contexts.domain.entities import Context
from src.contexts.domain.interfaces.context_uow import IContextUnitOfWork


context_create_dto = ContextCreateDTO(user_id="user")


@pytest.mark.asyncio
async def test_create_context(fake_context_uow: IContextUnitOfWork):
    await _create_context(fake_context_uow)


@pytest.mark.asyncio
async def test_get_context(fake_context_uow: IContextUnitOfWork):
    context = await _create_context(fake_context_uow)
    result = await get_context(context.id, fake_context_uow)
    assert result.id == context.id
    assert result.user_id == context.user_id

@pytest.mark.asyncio
async def test_get_unexsisting_context(fake_context_uow: IContextUnitOfWork):
    with pytest.raises(HTTPException) as exc:
        await get_context(uuid4(), fake_context_uow)
    assert exc.errisinstance(HTTPException)


@pytest.mark.asyncio
async def test_delete_context(fake_context_uow: IContextUnitOfWork):
    context = await _create_context(fake_context_uow)
    await delete_context(context.id, fake_context_uow)


@pytest.mark.asyncio
async def test_delete_unexisting_context(fake_context_uow: IContextUnitOfWork):
    with pytest.raises(HTTPException) as exc:
        await delete_context(uuid4(), fake_context_uow)
    assert exc.errisinstance(HTTPException)


async def _create_context(context_uow: IContextUnitOfWork) -> ContextReadDTO:
    context = await create_context(context_create_dto, context_uow)
    assert context.user_id == context_create_dto.user_id
    return context
