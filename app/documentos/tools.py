from app.agente.tools.base import Tool, ToolContext
from app.documentos.embedder import Embedder
from app.documentos.vector_store import VectorStore

def build_buscar_documentos_tool(embedder: Embedder, vector_store: VectorStore) -> Tool:
    async def _handler(ctx: ToolContext, args: dict) -> str:
        consulta = args["consulta"]
        vector = (await embedder.embed([consulta]))[0]
        hits = vector_store.search(vector=vector, user_external_id=ctx.user_external_id, top_k=5)
        if not hits:
            return "Sin resultados en los documentos subidos."
        return "Fragmentos encontrados:\n" + "\n".join(f"- {h.text}" for h in hits)

    return Tool(
        name="buscar_en_documentos",
        description="Busca información en los documentos (PDF/Excel) que el usuario ha subido.",
        parameters={
            "type": "object",
            "properties": {"consulta": {"type": "string", "description": "Qué buscar en los documentos"}},
            "required": ["consulta"],
            "additionalProperties": False,
        },
        permission="documentos:read",
        handler=_handler,
    )
