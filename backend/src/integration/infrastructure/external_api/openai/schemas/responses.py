from pydantic import BaseModel


class OpenAIResponse(BaseModel):
    content: str
    remaining_requests: int | None = None
    remaining_tokens: int | None = None
    reset_in: str | None = None
