from app.auth.roles import Role, has_permission

def test_admin_has_all():
    assert has_permission(Role.ADMIN, "facturas:read")
    assert has_permission(Role.ADMIN, "anything:whatever")

def test_administracion_reads_facturas():
    assert has_permission(Role.ADMINISTRACION, "facturas:read")

def test_produccion_cannot_read_facturas():
    assert not has_permission(Role.PRODUCCION, "facturas:read")

def test_lectura_is_read_only():
    assert has_permission(Role.LECTURA, "facturas:read")
    assert not has_permission(Role.LECTURA, "facturas:write")
