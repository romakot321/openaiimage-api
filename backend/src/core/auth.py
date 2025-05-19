from fastapi import HTTPException
from fastapi import Header
from src.core.config import settings


def validate_api_token(api_token: str = Header()):
    if api_token != settings.API_TOKEN:
        raise HTTPException(401, detail="Invalid Api-Token")
