from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from fastapi_storages.integrations.sqlalchemy import ImageType
from src.db.base import Base, BaseMixin
from src.core.filesystem_storage import storage


class ModelDB(BaseMixin, Base):
    __tablename__ = "prompts"

    text: Mapped[str]
    title: Mapped[str]
    is_model: Mapped[bool]
    for_image: Mapped[bool]
    for_video: Mapped[bool]
    image: Mapped[ImageType | None] = mapped_column(type_=ImageType(storage=storage), nullable=True)
    category_name: Mapped[str | None] = mapped_column(ForeignKey("prompt_categories.name", ondelete="CASCADE"))

    user_inputs: Mapped[list['ModelUserInputDB']] = relationship(back_populates="model", lazy="selectin")
    category: Mapped['ModelCategoryDB'] = relationship(back_populates="models", lazy="noload")

    def __str__(self) -> str:
        return f"model {self.title}"


class ModelUserInputDB(Base):
    __tablename__ = "prompt_userinputs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    prompt_id: Mapped[int] = mapped_column(ForeignKey("prompts.id", ondelete="CASCADE"))
    key: Mapped[str]
    description: Mapped[str]

    model: Mapped['ModelDB'] = relationship(back_populates="user_inputs", lazy="noload")

    def __str__(self) -> str:
        return f"Input {self.description}"



class ModelCategoryDB(BaseMixin, Base):
    __tablename__ = "prompt_categories"

    name: Mapped[str] = mapped_column(unique=True)

    models: Mapped[list["ModelDB"]] = relationship(back_populates="category", lazy="selectin")

    def __str__(self) -> str:
        return f"Category {self.name}"

