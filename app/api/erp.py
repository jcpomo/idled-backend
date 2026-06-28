from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.audit.service import record
from app.auth.dependencies import get_current_user, require_permission
from app.auth.models import User
from app.core.db import get_session
from app.erp_gateway.base import ERPGateway, Factura
from app.erp_gateway.dependencies import get_erp_gateway

router = APIRouter(prefix="/api/erp", tags=["erp"])

@router.get(
    "/facturas-pendientes",
    response_model=list[Factura],
    dependencies=[Depends(require_permission("facturas:read"))],
)
async def facturas_pendientes(
    authorization: str = Header(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    erp: ERPGateway = Depends(get_erp_gateway),
) -> list[Factura]:
    token = authorization.removeprefix("Bearer ").strip()
    facturas = await erp.facturas_pendientes(token=token)
    await record(
        session,
        user_external_id=user.external_id,
        action="facturas_pendientes",
        tool="erp.facturas_pendientes",
        params={"count": len(facturas)},
        result_summary=f"{len(facturas)} facturas",
    )
    return facturas
