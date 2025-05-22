import httpx
import pytest
from src.users.domain.dtos import UserCreateDTO

user_data = UserCreateDTO(user_id="test", app_bundle="test")


@pytest.mark.asyncio(loop_scope="session")
async def test_create_and_login_and_getme(client: httpx.AsyncClient):
    response = await client.post("/api/v2/user", json=user_data.model_dump())
    assert response.status_code == 200, response.text

    response = await client.post("/api/v2/auth/login", json=user_data.model_dump())
    assert response.status_code == 200, response.text
    body = response.json()
    assert body.get("api_token") is not None

    response = await client.get("/api/v2/auth/me", headers={"Api-Token": body["api_token"]})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body.get("user_id") == user_data.user_id and body.get("app_bundle") == user_data.app_bundle

