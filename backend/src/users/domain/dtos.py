from pydantic import AliasChoices, BaseModel, Field


class UserReadDTO(BaseModel):
    user_id: str
    app_bundle: str
    tokens: int


class UserCreateDTO(BaseModel):
    user_id: str = Field(validation_alias=AliasChoices("user_id", "external_id"))
    app_bundle: str
