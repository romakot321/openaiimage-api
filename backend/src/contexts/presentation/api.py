from uuid import UUID
from fastapi import APIRouter

from src.contexts.application.use_cases.context_create import create_context
from src.contexts.application.use_cases.context_get import get_context as uc_get_context
from src.contexts.application.use_cases.context_delete import delete_context as uc_delete_context
from src.contexts.domain.dtos import ContextCreateDTO, ContextReadDTO
from src.contexts.presentation.dependencies import ContextUoWDepend

router = APIRouter()


@router.post("", response_model=ContextReadDTO)
async def create_new_context(schema: ContextCreateDTO, uow: ContextUoWDepend):
    return await create_context(schema, uow)


@router.get("/{context_id}", response_model=ContextReadDTO)
async def get_context(context_id: UUID, uow: ContextUoWDepend):
    return await uc_get_context(context_id, uow)


@router.delete("/{context_id}", status_code=204)
async def delete_context(context_id: UUID, uow: ContextUoWDepend):
    await uc_delete_context(context_id, uow)
