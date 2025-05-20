from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column
from uuid import UUID

from src.db.base import Base, BaseMixin


class TaskItemDB(Base):
    __tablename__ = "task_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    task_id: Mapped[UUID] = mapped_column(ForeignKey('tasks.id', ondelete="CASCADE"))
    result_url: Mapped[str]
    used_tokens: Mapped[int] = mapped_column(server_default="0")

    task: Mapped['TaskDB'] = relationship(back_populates='items')


class TaskDB(BaseMixin, Base):
    __tablename__ = "tasks"

    error: Mapped[str | None] = mapped_column(nullable=True)
    context_id: Mapped[UUID | None] = mapped_column(ForeignKey("contexts.id", ondelete="CASCADE"))
    user_id: Mapped[str]
    app_bundle: Mapped[str]

    items: Mapped[list['TaskItemDB']] = relationship(back_populates='task', lazy='joined', cascade="all,delete")
    #images: Mapped[list['TaskImage']] = relationship(back_populates="task", lazy='selectin', cascade="all,delete")
    context: Mapped['ContextDB'] = relationship(back_populates="tasks", lazy="noload")

