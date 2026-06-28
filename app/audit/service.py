from sqlalchemy.ext.asyncio import AsyncSession
from app.audit.models import AuditLog

async def record(
    session: AsyncSession,
    user_external_id: str,
    action: str,
    tool: str | None = None,
    params: dict | None = None,
    result_summary: str | None = None,
) -> None:
    session.add(AuditLog(
        user_external_id=user_external_id,
        action=action,
        tool=tool,
        params=params or {},
        result_summary=result_summary,
    ))
    await session.commit()
