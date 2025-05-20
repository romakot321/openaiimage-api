from io import BytesIO
from typing import AsyncIterator

from PIL import Image
import httpx
import pytest
import pytest_asyncio

from src.main import app

from tests.fakes.context import FakeContextUnitOfWork
from tests.fakes.task import FakeTaskUnitOfWork


@pytest_asyncio.fixture(loop_scope="session")
async def client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://testserver', headers={"Api-Token": "123"}) as client:
        yield client


@pytest.fixture
def fake_test_uow():
    return FakeTaskUnitOfWork()


@pytest.fixture
def fake_context_uow():
    return FakeContextUnitOfWork()


@pytest.fixture
def mock_image() -> BytesIO:
    im = Image.new("RGB", (50, 50))
    buffer = BytesIO()
    buffer.name = "tmp.jpg"
    im.save(buffer)
    buffer.seek(0)
    return buffer
