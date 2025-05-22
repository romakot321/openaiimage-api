from pydantic import BaseModel


class AuthLoginDTO(BaseModel):
    user_id: str
    app_bundle: str


class AuthTokenDTO(BaseModel):
    api_token: str

