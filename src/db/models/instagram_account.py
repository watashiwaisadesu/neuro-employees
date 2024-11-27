from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, TIMESTAMP
from typing import Optional
import datetime

from src.core.database_setup import Base

class InstagramAccount(Base):
    __tablename__ = "instagram_accounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    instagram_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    page_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    expires_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, nullable=True)

    def __repr__(self):
        return (
            f"<InstagramAccount(id={self.id}, instagram_id={self.instagram_id}, "
            f"username={self.username})>"
        )

        )
