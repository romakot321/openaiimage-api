from loguru import logger
from socket import AF_INET

import aiohttp
from aiohttp.client import _RequestOptions

from src.tasks.domain.interfaces.http_client import IAsyncHttpClient

SIZE_POOL_AIOHTTP = 100


class AiohttpClient(IAsyncHttpClient[aiohttp.ClientResponse]):
    aiohttp_client: aiohttp.ClientSession | None = None
    log = logger

    @classmethod
    def get_aiohttp_client(cls) -> aiohttp.ClientSession:
        if cls.aiohttp_client is None:
            cls.log.debug("Initialize AiohttpClient session.")
            timeout = aiohttp.ClientTimeout(total=2)
            connector = aiohttp.TCPConnector(
                family=AF_INET,
                limit_per_host=SIZE_POOL_AIOHTTP,
            )
            cls.aiohttp_client = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
            )

        return cls.aiohttp_client

    @classmethod
    async def close_aiohttp_client(cls) -> None:
        if cls.aiohttp_client:
            cls.log.debug("Close AiohttpClient session.")
            await cls.aiohttp_client.close()
            cls.aiohttp_client = None

    @classmethod
    async def get(cls, url: str, **kwargs: _RequestOptions) -> aiohttp.ClientResponse:
        client = cls.get_aiohttp_client()

        cls.log.debug(f"Started GET {url}")
        response = await client.get(url, **kwargs)
        return response

    @classmethod
    async def post(cls, url: str, **kwargs: _RequestOptions) -> aiohttp.ClientResponse:
        client = cls.get_aiohttp_client()

        cls.log.debug(f"Started POST: {url}")
        response = await client.post(url, **kwargs)
        return response

    @classmethod
    async def put(cls, url: str, **kwargs: _RequestOptions) -> aiohttp.ClientResponse:
        client = cls.get_aiohttp_client()

        cls.log.debug(f"Started PUT: {url}")
        response = await client.put(url, **kwargs)
        return response

    @classmethod
    async def delete(cls, url: str, **kwargs: _RequestOptions) -> aiohttp.ClientResponse:
        client = cls.get_aiohttp_client()

        cls.log.debug(f"Started DELETE: {url}")
        response = await client.delete(url, **kwargs)
        return response

    @classmethod
    async def patch(cls, url: str, **kwargs: _RequestOptions) -> aiohttp.ClientResponse:
        client = cls.get_aiohttp_client()

        cls.log.debug(f"Started PATCH: {url}")
        response = await client.patch(url, **kwargs)
        return response
