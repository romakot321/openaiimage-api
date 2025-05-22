from fastapi import Depends
import httpx
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from src.contexts.domain.dtos import ContextCreateDTO
from src.db.dependencies import get_async_session
from tests.fakes.db import InMemoryDatabase
from tests.utils import override_dependencies

context_create_dto = ContextCreateDTO(user_id="user")


@pytest.mark.asyncio(loop_scope="session")
async def test_create_and_get(client: httpx.AsyncClient):
    context = await _create(client)
    assert context["user_id"] == context_create_dto.user_id

    response = await client.get(f"/api/context/{context['id']}")
    assert response.status_code == 200
    getted_context = response.json()
    assert context["id"] == getted_context["id"]


@pytest.mark.asyncio(loop_scope="session")
async def test_create_and_delete(client: httpx.AsyncClient):
    context = await _create(client)
    assert context["user_id"] == context_create_dto.user_id

    response = await client.delete(f"/api/context/{context['id']}")
    assert response.status_code == 204


@pytest.mark.asyncio(loop_scope="session")
async def test_create_and_add_task(client: httpx.AsyncClient):
    context = await _create(client)

    response = await client.post(
        "/api/task/text",
        json={
            "user_prompt": "test",
            "user_id": "test",
            "app_bundle": "test",
            "size": "1024x1024",
            "quality": "auto",
            "context_id": context["id"],
        },
    )
    assert response.status_code == 200, response.text
    task = response.json()
    assert task.get("id") is not None

    response = await client.get(f"/api/context/{context['id']}")
    body = response.json()
    assert body.get("id") == context["id"]
    assert body.get('tasks') and body["tasks"][0].get("id") == task["id"]


async def _create(client: httpx.AsyncClient) -> dict:
    response = await client.post("/api/context", json=context_create_dto.model_dump())
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == context_create_dto.user_id
    assert data.get("id") is not None
    return data
