from enum import Enum
from io import BytesIO
from pydantic import BaseModel, ConfigDict


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
