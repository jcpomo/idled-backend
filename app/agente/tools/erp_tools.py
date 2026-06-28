from app.agente.tools.base import Tool, ToolContext

async def _facturas_handler(ctx: ToolContext, args: dict) -> str:
    facturas = await ctx.erp.facturas_pendientes(token=ctx.token)
    if not facturas:
        return "No hay facturas pendientes."
    lineas = [f"- {f.id} | {f.cliente} | {f.total:.2f}€ | vence {f.vencimiento}" for f in facturas]
    return "Facturas pendientes:\n" + "\n".join(lineas)

def build_factura_tool() -> Tool:
    return Tool(
        name="facturas_pendientes",
        description="Devuelve las facturas pendientes de cobro (no pagadas).",
        parameters={"type": "object", "properties": {}, "additionalProperties": False},
        permission="facturas:read",
        handler=_facturas_handler,
    )

async def _stock_handler(ctx: ToolContext, args: dict) -> str:
    art = await ctx.erp.stock_articulo(token=ctx.token, referencia=args["referencia"])
    if art is None:
        return f"Artículo '{args['referencia']}' no encontrado."
    return f"{art.referencia} ({art.descripcion}): stock {art.stock}."

def build_stock_tool() -> Tool:
    return Tool(
        name="stock_articulo",
        description="Devuelve el stock de un artículo por su referencia.",
        parameters={
            "type": "object",
            "properties": {"referencia": {"type": "string", "description": "Referencia del artículo"}},
            "required": ["referencia"],
            "additionalProperties": False,
        },
        permission="stock:read",
        handler=_stock_handler,
    )
