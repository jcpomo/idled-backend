import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.db import Base
import app.audit.models  # noqa: F401 — registers AuditLog with Base.metadata
import app.auth.models   # noqa: F401 — registers User with Base.metadata
import app.agente.models  # noqa: F401 — registers AiConversation/AiMessage with Base.metadata

@pytest_asyncio.fixture
async def session() -> AsyncSession:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as s:
        yield s
    await engine.dispose()
