from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    DIRECCION = "direccion"
    COMERCIAL = "comercial"
    ADMINISTRACION = "administracion"
    PRODUCCION = "produccion"
    COMPRAS_ALMACEN = "compras_almacen"
    LECTURA = "lectura"

# permission = "<recurso>:<accion>"; admin se trata como comodín en has_permission
ROLE_PERMISSIONS: dict[Role, set[str]] = {
    Role.ADMIN: set(),  # comodín, ver has_permission
    Role.DIRECCION: {
        "facturas:read", "compras:read", "ventas:read", "stock:read", "kpis:read",
        "documentos:read",
    },
    Role.COMERCIAL: {
        "clientes:read", "pedidos:read", "ventas:read", "stock:read",
        "documentos:read", "documentos:write",
    },
    Role.ADMINISTRACION: {
        "facturas:read", "facturas:write", "cobros:read",
        "compras:read", "ventas:read", "documentos:read", "documentos:write",
    },
    Role.PRODUCCION: {
        "ordenes:read", "tiempos:read", "componentes:read",
        "documentos:read", "documentos:write",
    },
    Role.COMPRAS_ALMACEN: {
        "stock:read", "proveedores:read", "compras:read", "ofertas:read",
        "documentos:read", "documentos:write",
    },
    Role.LECTURA: {
        "facturas:read", "compras:read", "ventas:read", "stock:read", "clientes:read",
        "documentos:read",
    },
}

def has_permission(role: Role, permission: str) -> bool:
    if role == Role.ADMIN:
        return True
    return permission in ROLE_PERMISSIONS.get(role, set())
