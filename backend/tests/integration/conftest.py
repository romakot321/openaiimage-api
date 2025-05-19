from typing import AsyncGenerator
import httpx
import pytest
import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from src.contexts.domain.dtos import ContextCreateDTO
from src.db.dependencies import get_async_session
from src.tasks.domain.interfaces.task_source_client import ITaskSourceClient
from tests.fakes.task_source import FakeTaskSourceClient
from tests.utils import override_dependencies
# from tests.fakes.db import async_session, create_tables, engine


TABLES_TO_TRUNCATE = [
    "tasks",
    "contexts",
]


@pytest.fixture
def context_factory():
    async def _create(client: httpx.AsyncClient, dto: ContextCreateDTO) -> dict:
        response = await client.post("/api/context", json=dto.model_dump())
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == dto.user_id
        return data
    return _create


@pytest.fixture
def fake_task_source() -> ITaskSourceClient:
    print("FAKETASKSOURCE")
    return FakeTaskSourceClient()
