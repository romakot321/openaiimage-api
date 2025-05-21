from uuid import UUID
from sqlalchemy import ForeignKey, Table, func, select
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship
from fastapi_storages.integrations.sqlalchemy import ImageType
from src.db.base import Base, BaseMixin
from src.core.filesystem_storage import storage


class ModelUserInputAssociationDB(Base):
    __tablename__ = "prompts_userinputs_association"

    id: Mapped[int] = mapped_column(primary_key=True)
    prompt_id: Mapped[UUID] = mapped_column(ForeignKey("prompts.id"))
    prompt_userinput_id: Mapped[int] = mapped_column(ForeignKey("prompt_userinputs.id"))


class ModelDB(BaseMixin, Base):
    __tablename__ = "prompts"

    text: Mapped[str]
    title: Mapped[str]
    is_model: Mapped[bool]
    for_image: Mapped[bool]
    for_video: Mapped[bool]
    position: Mapped[int | None]
    image: Mapped[ImageType | None] = mapped_column(type_=ImageType(storage=storage), nullable=True)
    category_name: Mapped[str | None] = mapped_column(ForeignKey("prompt_categories.name", ondelete="CASCADE"))

    user_inputs: Mapped[list['ModelUserInputDB']] = relationship(back_populates="model", lazy="selectin", secondary="prompts_userinputs_association")
    category: Mapped['ModelCategoryDB'] = relationship(back_populates="models", lazy="selectin")
    tasks: Mapped[list["TaskDB"]] = relationship(back_populates="model", lazy="selectin")

    def __str__(self) -> str:
        return f"model {self.title}"

    @hybrid_property
    def tasks_count(self):
        return len(self.tasks)

    @tasks_count.expression
    @classmethod
    def tasks_count(cls):
        return select(func.count()).select_from(cls.tasks)


class ModelUserInputDB(Base):
    __tablename__ = "prompt_userinputs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    key: Mapped[str]
    description: Mapped[str]

    model: Mapped[list['ModelDB']] = relationship(back_populates="user_inputs", lazy="selectin", secondary="prompts_userinputs_association")

    def __str__(self) -> str:
        return f"Input {self.description}"


class ModelCategoryDB(BaseMixin, Base):
    __tablename__ = "prompt_categories"

    name: Mapped[str] = mapped_column(unique=True, primary_key=True)
    position: Mapped[int | None]

    models: Mapped[list["ModelDB"]] = relationship(back_populates="category", lazy="selectin")

    def __str__(self) -> str:
        return f"Category {self.name}"

