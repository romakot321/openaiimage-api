from enum import Enum
from io import BytesIO
from pydantic import BaseModel, ConfigDict


class ExternalImageSize(Enum):
    sm = "256x256"
    md = "512x512"
    lg = "1024x1024"


class ExternalImage2ImageTaskSchema(BaseModel):
    prompt: str
    size: ExternalImageSize
    image: BytesIO

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ExternalText2ImageTaskSchema(BaseModel):
    prompt: str
    size: ExternalImageSize

    model_config = ConfigDict(arbitrary_types_allowed=True)
