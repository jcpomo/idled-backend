from app.auth.models import User
from app.audit.models import AuditLog


def test_user_table_columns():
    cols = set(User.__table__.columns.keys())
    assert {"id", "external_id", "name", "role", "created_at"} <= cols


def test_audit_table_columns():
    cols = set(AuditLog.__table__.columns.keys())
    assert {"id", "user_external_id", "action", "tool", "params", "created_at"} <= cols
