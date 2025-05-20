from io import BytesIO
import httpx
import pytest
from src.tasks.domain.dtos import TaskCreateImageDTO, TaskCreateTextDTO
from src.tasks.domain.entities import TaskResultSize

toimage_create_dto = TaskCreateImageDTO(user_id="test", app_bundle="test", size=TaskResultSize.square, user_prompt="test prompt")
totext_create_dto = TaskCreateTextDTO(user_id="test", app_bundle="test", prompt="test prompt")


@pytest.mark.asyncio(loop_scope="session")
async def test_create_image2image(client: httpx.AsyncClient, mock_image: BytesIO):
    response = await client.post(
        "/api/task/image",
        files={"file": ("tmp.jpg", mock_image, "image/jpg")},
        data=toimage_create_dto.model_dump(mode="json", exclude_unset=True)
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body.get("id") is not None


@pytest.mark.asyncio(loop_scope="session")
async def test_create_text2image(client: httpx.AsyncClient):
    response = await client.post(
        "/api/task/text",
        json=toimage_create_dto.model_dump(mode="json", exclude_unset=True)
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body.get("id") is not None


@pytest.mark.asyncio(loop_scope="session")
async def test_create_text2text(client: httpx.AsyncClient):
    response = await client.post("/api/task/text/text", json=totext_create_dto.model_dump())
    assert response.status_code == 200, response.text
    body = response.json()
    assert body.get("id") is not None


@pytest.mark.asyncio(loop_scope="session")
async def test_get_task(client: httpx.AsyncClient):
    response = await client.post("/api/task/text/text", json=totext_create_dto.model_dump())
    assert response.status_code == 200, response.text
    task = response.json()
    assert task.get("id") is not None

    response = await client.get(f"/api/task/{task['id']}")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body.get('id') == task['id'] and body.get('error') is None


@pytest.mark.asyncio(loop_scope="session")
async def test_get_statistics(client: httpx.AsyncClient):
    response = await client.get("/api/task/statistics")
    assert response.status_code == 200
    body = response.json()
    assert body.get("remaining_tokens") is not None and body.get("remaining_requests") is not None

