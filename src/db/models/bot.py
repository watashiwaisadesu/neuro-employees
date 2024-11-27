import uuid
from sqlalchemy import String, Text, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from src.core.database_setup import Base  # Assuming `Base` is defined using `declarative_base()`

class Bot(Base):
    __tablename__ = "bots"

    uid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_uid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.uid"), nullable=False)
    bot_type: Mapped[str] = mapped_column(String, nullable=False)  # Тип бота
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    context: Mapped[str | None] = mapped_column(Text, nullable=True)
    creativity: Mapped[float] = mapped_column(Float, default=0.5)
    status: Mapped[str] = mapped_column(String, default="draft")  # "draft", "active"
    integration_token: Mapped[str | None] = mapped_column(String, nullable=True)  # Токен интеграции

    def __repr__(self) -> str:
        return f"<Bot name={self.name} type={self.bot_type} status={self.status}>"
