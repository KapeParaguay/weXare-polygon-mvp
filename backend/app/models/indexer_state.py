from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class IndexerState(Base):
    __tablename__ = "indexer_state"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String, unique=True, index=True)
    value: Mapped[str] = mapped_column(String)
