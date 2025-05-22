from sqlalchemy.orm import Mapped, mapped_column
from src.db.base import Base, BaseMixin


class UserDB(BaseMixin, Base):
    __tablename__ = "users"

    external_id: Mapped[str] = mapped_column(index=True)
    app_bundle: Mapped[str]
    tokens: Mapped[int]
