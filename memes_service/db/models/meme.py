import uuid
from datetime import datetime

from sqlalchemy import String, UUID, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base

class Meme(Base):
    __tablename__ = 'meme'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    description: Mapped[str | None] = mapped_column(String(255))
    image_url: Mapped[str] = mapped_column(String(255))
    image_name: Mapped[str] = mapped_column(String(255))
    created_datetime: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
