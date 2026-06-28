from app.auth.jwt import TokenPayload
from app.auth.roles import Role
from app.auth.service import upsert_user

async def test_upsert_creates_then_updates(session):
    p1 = TokenPayload(user_id="ext-9", role=Role.COMERCIAL, name="Leo")
    u1 = await upsert_user(session, p1)
    assert u1.external_id == "ext-9"
    assert u1.role == "comercial"

    p2 = TokenPayload(user_id="ext-9", role=Role.ADMINISTRACION, name="Leo R.")
    u2 = await upsert_user(session, p2)
    assert u2.id == u1.id           # same row
    assert u2.role == "administracion"
    assert u2.name == "Leo R."
