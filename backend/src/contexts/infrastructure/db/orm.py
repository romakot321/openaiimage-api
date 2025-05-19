from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.contexts.domain.entities import ContextEntityContentType
from src.db.base import Base, BaseMixin


class ContextDB(BaseMixin, Base):
    __tablename__ = "contexts"

    user_id: Mapped[str]
    entities: Mapped[list["ContextEntityDB"]] = relationship(back_populates="context", lazy="selectin", cascade="all,delete")
    tasks: Mapped[list["TaskDB"]] = relationship(back_populates="context", lazy="selectin", cascade="all,delete")


class ContextEntityDB(BaseMixin, Base):
    __tablename__ = "context_entitys"

    content_type: Mapped[ContextEntityContentType] = mapped_column(doc="text, image")
    content: Mapped[str] = mapped_column(doc="Prompt or image filename from storage")
    role: Mapped[str]
    context_id: Mapped[str] = mapped_column(ForeignKey("contexts.id", ondelete="CASCADE"))

    context: Mapped['ContextDB'] = relationship(back_populates="entities", lazy="noload")


