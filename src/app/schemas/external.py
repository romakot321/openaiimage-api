from pydantic import BaseModel


class ExternalTaskSchema(BaseModel):
    text: str
