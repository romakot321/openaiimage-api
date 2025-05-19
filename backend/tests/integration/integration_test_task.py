import asyncio
from io import BytesIO
import httpx
import pytest
import logging
from src.integration.presentation.dependencies import get_openai_adapter
from src.tasks.domain.dtos import TaskCreateImageDTO, TaskCreateTextDTO
from src.tasks.domain.entities import TaskResultSize
from src.tasks.domain.interfaces.task_source_client import ITaskSourceClient

from tests.utils import override_dependencies

logger = logging.getLogger(__name__)

create_dto = TaskCreateImageDTO(
    user_prompt="test prompt",
    user_id="test",
    app_bundle="prompt",
    size=TaskResultSize.square,
)


@pytest.mark.asyncio(loop_scope="session")
async def test_create_and_wait_for_result(
    client: httpx.AsyncClient, fake_task_source: ITaskSourceClient, mock_image: BytesIO
):
    task = await _create(client, fake_task_source, mock_image)
    async with override_dependencies({get_openai_adapter: lambda: fake_task_source}):
        while True:
            await asyncio.sleep(0.1)

            response = await client.get(f"/api/task/{task['id']}")
            assert response.status_code == 200

            body = response.json()
            assert body.get("error") is None and body.get("items") is not None

            if body.get("items"):
                break
    assert body["items"][0].get("result_url") and body["items"][0][
        "result_url"
    ].endswith(f"/api/task/{body['id']}/result"), "Invalid task result_url received"
    return
    with pytest.raises(FileNotFoundError) as exc:
        response = await client.get(f"/api/task/{body['id']}/result")
    if exc.type is FileNotFoundError:
        raise ValueError("Volume with images not connected")
    else:
        assert response.status_code == 200, response.text


async def _create(
    client: httpx.AsyncClient, task_source: ITaskSourceClient, image: BytesIO
) -> dict:
    async with override_dependencies({get_openai_adapter: lambda: task_source}):
        response = await client.post(
            "/api/task/image",
            files={"image": ("tmp.jpg", image, "image/jpg")},
            data=create_dto.model_dump(mode="json", exclude_unset=True),
        )
    assert response.status_code == 200

    data = response.json()
    logger.debug("CREATED", data)
    assert data.get("id") is not None
    return data
