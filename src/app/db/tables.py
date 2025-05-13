import datetime as dt
import uuid
from uuid import UUID
from enum import Enum, auto

from sqlalchemy import TEXT, LargeBinary, bindparam
from sqlalchemy import CheckConstraint
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Table
from sqlalchemy import text
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped as M
from sqlalchemy.orm import mapped_column as column
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import false
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.associationproxy import AssociationProxy

from sqlalchemy_service import Base
from sqlalchemy_service.base_db.base import ServiceEngine

sql_utcnow = text("(now() at time zone 'utc')")

engine = ServiceEngine()


class BaseMixin:
    @declared_attr.directive
    def __tablename__(cls):
        letters = ['_' + i.lower() if i.isupper() else i for i in cls.__name__]
        return ''.join(letters).lstrip('_') + 's'

    id: M[UUID] = column(server_default=text("gen_random_uuid()"), primary_key=True, index=True)
    created_at: M[dt.datetime] = column(server_default=sql_utcnow, default=dt.datetime.now)
    updated_at: M[dt.datetime | None] = column(nullable=True, onupdate=sql_utcnow)


class TaskStatus(Enum):
    queued = 'queued'
    finished = 'finished'
    error = 'error'


class TaskItem(Base):
    __tablename__ = "task_items"

    id: M[int] = column(primary_key=True, index=True, autoincrement=True)
    task_id: M[UUID] = column(ForeignKey('tasks.id', ondelete="CASCADE"))
    result_url: M[str | None]

    task: M['Task'] = relationship(back_populates='items')


class Task(BaseMixin, Base):
    error: M[str | None] = column(nullable=True)
    context_id: M[UUID | None] = column(ForeignKey("contexts.id", ondelete="CASCADE"))
    user_id: M[str]
    app_bundle: M[str]

    items: M[list['TaskItem']] = relationship(back_populates='task', lazy='selectin', cascade="all,delete")
    images: M[list['TaskImage']] = relationship(back_populates="task", lazy='selectin', cascade="all,delete")
    context: M['Context'] = relationship(back_populates="tasks", lazy="noload")


class PromptUserInput(Base):
    __tablename__ = "prompt_userinputs"

    id: M[int] = column(primary_key=True, index=True, autoincrement=True)
    prompt_id: M[int] = column(ForeignKey("prompts.id", ondelete="CASCADE"))
    key: M[str]
    description: M[str]

    prompt: M['Prompt'] = relationship(back_populates="user_inputs", lazy="noload")

    def __str__(self) -> str:
        return f"Input {self.description}"


class Prompt(BaseMixin, Base):
    text: M[str]
    title: M[str]
    is_model: M[bool]
    for_image: M[bool]
    for_video: M[bool]
    image: M[bytes | None] = column(type_=LargeBinary, nullable=True)
    category_name: M[str | None] = column(ForeignKey("prompt_categories.id", ondelete="CASCADE"))

    user_inputs: M[list['PromptUserInput']] = relationship(back_populates="prompt", lazy="selectin")
    category: M['PromptCategory'] = relationship(back_populates="prompts", lazy="noload")

    def __str__(self) -> str:
        return f"Prompt {self.title}"


class TaskImage(BaseMixin, Base):
    external_id: M[str]
    task_id: M[UUID] = column(ForeignKey("tasks.id", ondelete="CASCADE"))

    task: M['Task'] = relationship(back_populates='images')


class TaskRequest(BaseMixin, Base):
    id: M[int] = column(primary_key=True, index=True, autoincrement=True)
    task_id: M[UUID] = column(ForeignKey('tasks.id', ondelete="CASCADE"))
    schema: M[str]
    status: M[str | None]


class Context(BaseMixin, Base):
    user_id: M[str]

    entities: M[list["ContextEntity"]] = relationship(back_populates="context", lazy="selectin", cascade="all,delete")
    tasks: M[list["Task"]] = relationship(back_populates="context", lazy="selectin", cascade="all,delete")


class ContextEntityContentType(Enum):
    image = 'image'
    text = 'text'


class ContextEntityRole(Enum):
    user = 'user'
    assistant = 'assistant'
    system = 'system'


class ContextEntity(BaseMixin, Base):
    content_type: M[ContextEntityContentType]
    content: M[str] = column(doc="Prompt or image filename from storage")
    role: M[ContextEntityRole]
    context_id: M[str] = column(ForeignKey("contexts.id", ondelete="CASCADE"))

    context: M['Context'] = relationship(back_populates="entities", lazy="noload")


class PromptCategory(BaseMixin, Base):
    __tablename__ = "prompt_categories"

    name: M[str] = column(unique=True)

    prompts: M[list["Prompt"]] = relationship(back_populates="category", lazy="selectin")

    def __str__(self) -> str:
        return f"Category {self.name}"
