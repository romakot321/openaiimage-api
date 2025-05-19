import abc
from typing import Generic, TypeVar


TRequestForImage = TypeVar("TRequestForImage")
TRequestForText = TypeVar("TRequestForText")
TResponse = TypeVar("TResponse")


class ITaskSourceClient(abc.ABC, Generic[TRequestForImage, TRequestForText, TResponse]):
    webhook_domain: str | None

    @abc.abstractmethod
    async def generate_text2image(self, request: TRequestForImage) -> TResponse: ...

    @abc.abstractmethod
    async def generate_image2image(self, request: TRequestForImage) -> TResponse: ...

    @abc.abstractmethod
    async def generate_text2text(self, request: TRequestForText) -> TResponse: ...
