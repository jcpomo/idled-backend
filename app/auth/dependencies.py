from collections.abc import Callable
from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.jwt import InvalidTokenError, decode_token
from app.auth.models import User
from app.auth.roles import Role, has_permission
from app.auth.service import upsert_user
from app.core.db import get_session

async def get_current_user(
    authorization: str | None = Header(default=None),
    session: AsyncSession = Depends(get_session),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = decode_token(token)
    except InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    return await upsert_user(session, payload)

def require_permission(permission: str) -> Callable:
    async def _guard(user: User = Depends(get_current_user)) -> User:
        if not has_permission(Role(user.role), permission):
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return _guard
