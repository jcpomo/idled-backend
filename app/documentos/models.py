import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class Document(Base):
    __tablename__ = "documents"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_external_id: Mapped[str] = mapped_column(String, index=True)
    filename: Mapped[str] = mapped_column(String)
    content_type: Mapped[str] = mapped_column(String)
    storage_key: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="uploaded")
    error: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
