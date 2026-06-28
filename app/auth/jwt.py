import jwt as pyjwt
from pydantic import BaseModel
from app.auth.roles import Role
from app.core.config import get_settings

class InvalidTokenError(Exception):
    pass

class TokenPayload(BaseModel):
    user_id: str
    role: Role
    name: str | None = None

def decode_token(token: str) -> TokenPayload:
    settings = get_settings()
    try:
        claims = pyjwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except pyjwt.PyJWTError as exc:
        raise InvalidTokenError(str(exc)) from exc
    try:
        return TokenPayload(user_id=claims["sub"], role=claims["role"], name=claims.get("name"))
    except (KeyError, ValueError) as exc:
        raise InvalidTokenError(f"invalid claims: {exc}") from exc
