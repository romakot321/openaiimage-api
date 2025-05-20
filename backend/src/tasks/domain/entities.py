from enum import Enum
from pydantic import BaseModel, ConfigDict
from uuid import UUID


class TaskSource(Enum):
    openai = "openai"


class TaskResultQuality(Enum):
    high = "high"
    medium = "medium"
    low = "low"
    auto = "auto"


class TaskResultSize(Enum):
    square = "1024x1024"
    landscape = "1536x1024"
    portrait = "1024x1536"


class TaskItem(BaseModel):
    id: int
    result_url: str

    model_config = ConfigDict(from_attributes=True)


class Task(BaseModel):
    id: UUID
    user_id: str
    app_bundle: str
    context_id: UUID | None = None
    error: str | None = None
    items: list[TaskItem]


class TaskUserInput(BaseModel):
    key: str
    value: str


class TaskItemCreate(BaseModel):
    task_id: UUID
    result_url: str


class TaskCreate(BaseModel):
    user_id: str
    app_bundle: str
    context_id: UUID | str | None = None


class TaskUpdate(BaseModel):
    error: str | None = None


class TaskRun(BaseModel):
    user_prompt: str
    quality: TaskResultQuality
    size: TaskResultSize
    webhook_url: str | None = None
    context_id: UUID | str | None = None
    user_inputs: list[TaskUserInput]
    model_id: UUID | None = None
