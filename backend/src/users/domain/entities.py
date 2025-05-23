from enum import Enum
from uuid import UUID
from pydantic import BaseModel
import datetime as dt


class User(BaseModel):
    id: UUID
    external_id: str
    app_bundle: str
    tokens: int


class UserCreate(BaseModel):
    external_id: str
    app_bundle: str
    tokens: int = 0


class UserUpdate(BaseModel):
    tokens: int | None = None


class AppHudWebhookEventName(str, Enum):
    subscription_started = 'subscription_started'


class AppHudWebhook(BaseModel):
    class App(BaseModel):
        bundle_id: str
        package_name: str

    class Event(BaseModel):
        class EventProperties(BaseModel):
            currency: str
            usd_price: float
            product_id: str

        id: UUID
        created_at: dt.datetime
        properties: EventProperties
        name: str

    class User(BaseModel):
        user_id: UUID

    app: App
    event: Event
    user: User
