import httpx
import pytest
from src.users.domain.dtos import UserCreateDTO

create_dto = UserCreateDTO(user_id="test", app_bundle="test")


@pytest.mark.asyncio(loop_scope="session")
async def test_user_create(client: httpx.AsyncClient):
    response = await client.post("/api/v2/user", json=create_dto.model_dump())
    assert response.status_code == 200, response.text
    body = response.json()
    assert body.get("user_id") == create_dto.user_id and body.get("app_bundle") == create_dto.app_bundle
    assert body.get("tokens") is not None and body["tokens"] > 0
