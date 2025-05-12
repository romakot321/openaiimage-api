from enum import Enum
from io import BytesIO
from pydantic import BaseModel, ConfigDict, Field


class ExternalImageSize(Enum):
    square = "1024x1024"
    landscape = "1536x1024"
    portrait = "1024x1536"


class ExternalImageQuality(Enum):
    high = 'high'
    medium = 'medium'
    low = 'low'
    auto = 'auto'


class ExternalImage2ImageTaskSchema(BaseModel):
    prompt: str
    size: ExternalImageSize
    quality: ExternalImageQuality
    images: list[BytesIO]

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ExternalText2ImageTaskSchema(BaseModel):
    prompt: str
    quality: ExternalImageQuality
    size: ExternalImageSize

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ExternalText2TextTaskSchema(BaseModel):
    class TextMessage(BaseModel):
        role: str
        content: str

    class ImageMessage(BaseModel):
        class ImageContent(BaseModel):
            type: str = "input_image"
            image_url: str

        class TextContent(BaseModel):
            """Also used for image caption"""
            type: str = "input_text"
            text: str

        role: str
        content: list[ImageContent | TextContent]

    input: list[TextMessage | ImageMessage]
    model: str = "gpt-4.1"
    max_output_tokens: int = 4096


class ExternalResponse(BaseModel):
    content: str | None = None
    remaining_requests: int | None = None
    remaining_tokens: int | None = None
    reset_in: str | None = None
