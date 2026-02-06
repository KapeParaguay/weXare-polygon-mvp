from sqlalchemy import String, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

UserStatus = Enum("ACTIVE", "PAUSED", "VACATION", name="user_status")
UserRole = Enum("CREATOR", "WORKER", "JUDGE", name="user_role")


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    wallet_address: Mapped[str | None] = mapped_column(String, unique=True, index=True, nullable=True)
    status: Mapped[str] = mapped_column(UserStatus, default="ACTIVE")
    roles: Mapped[str] = mapped_column(String, default="CREATOR")
