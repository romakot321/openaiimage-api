import logging
from typing import Any, Callable, Coroutine
from fastapi import HTTPException
from pydantic import ValidationError
from src.users.domain.entities import AppHudWebhook, AppHudWebhookEventName, UserUpdate
from src.users.domain.interfaces.user_uow import IUserUnitOfWork
from src.core.config import settings

logger = logging.getLogger(__name__)


class AppHudWorker:
    _product_id_to_tokens: dict[str, int] = {
        "1000_Tokens_66.00": 1000,
        "100_Tokens_9.00": 100,
        "300_Tokens_23.00": 300,
        "week_6.99_not_trial": 50,
        "yearly_49.99_not_trial": 500
    }

    def __init__(self, user_uow: IUserUnitOfWork, x_apphud_token: str) -> None:
        if x_apphud_token != settings.APPHUD_SECRET_TOKEN:
            raise HTTPException(401)
        self.user_uow = user_uow

    async def process_webhook(self, webhook_data: dict):
        logger.info(f"Receive apphud webhook: {webhook_data}")
        webhook = self._parse_webhook(webhook_data)
        handler = self.recognize_webhook_handler(webhook)
        if handler is None:
            logger.info(f"Webhook without action received")
            return
        await handler

    def recognize_webhook_handler(self, webhook: AppHudWebhook) -> Coroutine[Any, Any, Any] | None:
        if webhook.event.name == AppHudWebhookEventName.subscription_started:
            return self._handle_subscription_started(webhook)

    async def _handle_subscription_started(self, webhook: AppHudWebhook) -> None:
        user_id, app_bundle = str(webhook.user.user_id).upper(), webhook.app.bundle_id
        product_tokens = self._map_product_id_to_tokens(webhook.event.properties.product_id)
        async with self.user_uow:
            user = await self.user_uow.users.get_by_external(user_id, app_bundle)
            request = UserUpdate(tokens=user.tokens + product_tokens)
            await self.user_uow.users.update_by_external(user_id, app_bundle, request)
            await self.user_uow.commit()
        logger.info(f"Apphud webhook: Added {product_tokens} tokens for user {user_id} from {app_bundle}")

    def _map_product_id_to_tokens(self, product_id: str) -> int:
        value = self._product_id_to_tokens.get(product_id)
        if value is None:
            raise ValueError(f"Failed to map product_id to tokens: Unknown {product_id=}")
        return value

    @staticmethod
    def _parse_webhook(webhook_data: dict) -> AppHudWebhook:
        try:
            return AppHudWebhook.model_validate(webhook_data)
        except ValidationError as e:
            logger.warning(f"Receive invalid apphud webhook: {webhook_data}\nReason: {e}")
            raise HTTPException(422)
