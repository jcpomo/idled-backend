from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.jwt import TokenPayload
from app.auth.models import User

async def upsert_user(session: AsyncSession, payload: TokenPayload) -> User:
    result = await session.execute(select(User).where(User.external_id == payload.user_id))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(external_id=payload.user_id, name=payload.name, role=payload.role.value)
        session.add(user)
    else:
        user.name = payload.name
        user.role = payload.role.value
    await session.commit()
    await session.refresh(user)
    return user
