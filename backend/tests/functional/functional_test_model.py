import httpx
import pytest


@pytest.mark.asyncio(loop_scope="session")
async def test_list_models(client: httpx.AsyncClient):
    response = await client.get("/api/model")
    assert response.status_code == 200
