from src.tasks.domain.dtos import TaskReadDTO
from src.tasks.domain.entities import Task
from src.tasks.domain.interfaces.http_client import IAsyncHttpClient
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class TaskWebhookClient:
    def __init__(self, client: IAsyncHttpClient) -> None:
        self.client = client

    def _validate_webhook_url(self, webhook_url: str) -> bool:
        try:
            result = urlparse(webhook_url)
            return all([result.scheme, result.netloc])
        except AttributeError:
            return False

    async def send_webhook(self, task: Task, webhook_url: str) -> None:
        if not self._validate_webhook_url(webhook_url):
            logger.warning(f"Failed to send webhook: invalid {webhook_url=}")
            return
        schema = TaskReadDTO.model_validate(task.model_dump())
        response = await self.client.post(webhook_url, json=schema.model_dump(mode="json"))
        if response.status // 100 != 2:
            logger.warning("Failed to send webhook: unexpected response: " + await response.text())
        logger.info(f"Sended webhook for task {task.id}")
