import uuid
from datetime import datetime
from sqlalchemy import JSON, String, DateTime, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_external_id: Mapped[str] = mapped_column(String, index=True)
    action: Mapped[str] = mapped_column(String)
    tool: Mapped[str | None] = mapped_column(String, nullable=True)
    params: Mapped[dict] = mapped_column(JSON, default=dict)
    result_summary: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
