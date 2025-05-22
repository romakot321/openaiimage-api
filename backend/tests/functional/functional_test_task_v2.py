from io import BytesIO
import httpx
import pytest
from src.tasks.domain.dtos import TaskCreateImageDTO, TaskCreateTextDTO
from src.tasks.domain.entities import TaskResultSize
from src.users.domain.dtos import UserCreateDTO

toimage_create_dto = TaskCreateImageDTO(
    user_id="test",
    app_bundle="test",
    size=TaskResultSize.square,
    user_prompt="test prompt",
)
totext_create_dto = TaskCreateTextDTO(
    user_id="test", app_bundle="test", prompt="test prompt"
)
user_create_dto = UserCreateDTO(user_id="test", app_bundle="test")


async def _login(client: httpx.AsyncClient) -> dict:
    response = await client.post("/api/v2/user", json=user_create_dto.model_dump())
    assert response.status_code == 200, response.text
    response = await client.post("/api/v2/auth/login", json=user_create_dto.model_dump())
    assert response.status_code == 200, response.text
    body = response.json()
    return {'Api-Token': body.get("api_token")}


@pytest.mark.asyncio(loop_scope="session")
async def test_create_image2image(client: httpx.AsyncClient, mock_image: BytesIO):
    response = await client.post(
        "/api/v2/task/image",
        files={"file": ("tmp.jpg", mock_image, "image/jpg")},
        data=toimage_create_dto.model_dump(mode="json", exclude_unset=True),
        headers=await _login(client)
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body.get("id") is not None


@pytest.mark.asyncio(loop_scope="session")
async def test_create_text2image(client: httpx.AsyncClient):
    response = await client.post(
        "/api/v2/task/text",
        json=toimage_create_dto.model_dump(mode="json", exclude_unset=True),
        headers=await _login(client)
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body.get("id") is not None


@pytest.mark.asyncio(loop_scope="session")
async def test_create_text2text(client: httpx.AsyncClient):
    response = await client.post(
        "/api/v2/task/text/text",
        json=totext_create_dto.model_dump(),
        headers=await _login(client),
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body.get("id") is not None


@pytest.mark.asyncio(loop_scope="session")
async def test_get_task(client: httpx.AsyncClient):
    token_header = await _login(client)
    response = await client.post(
        "/api/v2/task/text/text",
        json=totext_create_dto.model_dump(),
        headers=token_header,
    )
    assert response.status_code == 200, response.text
    task = response.json()
    assert task.get("id") is not None

    response = await client.get(f"/api/v2/task/{task['id']}", headers=token_header)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body.get("id") == task["id"] and body.get("error") is None
