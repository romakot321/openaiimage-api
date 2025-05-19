from pydantic import BaseModel


class OpenAIResponse(BaseModel):
    content: str
    used_tokens: int | None = None
    remaining_requests: int | None = None
    remaining_tokens: int | None = None
    reset_in: str | None = None
