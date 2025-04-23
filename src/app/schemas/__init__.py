from pydantic import BaseModel


class BaseSearchSchema(BaseModel):
    page: int = 0
    count: int = 50
