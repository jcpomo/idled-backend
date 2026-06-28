import json
import uuid
from collections.abc import AsyncIterator
from fastapi import APIRouter, Depends, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.agente.orchestrator import AgentOrchestrator
from app.agente.model_config import build_provider_for, get_profile
from app.agente.service import append_message, get_or_create_conversation, load_history
from app.agente.tools.base import ToolContext
from app.agente.tools.registry import build_default_registry
from app.audit.service import record
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.auth.roles import Role
from app.core.db import get_session
from app.erp_gateway.base import ERPGateway
from app.erp_gateway.dependencies import get_erp_gateway

router = APIRouter(prefix="/api", tags=["chat"])

class ChatBody(BaseModel):
    message: str
    conversation_id: str | None = None

def get_orchestrator() -> AgentOrchestrator:
    return AgentOrchestrator(
        provider=build_provider_for("chat"),
        registry=build_default_registry(),
    )

def _chunk(text: str, size: int = 512) -> list[str]:
    return [text[i:i + size] for i in range(0, len(text), size)] or [""]

@router.post("/chat")
async def chat(
    body: ChatBody,
    authorization: str = Header(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    erp: ERPGateway = Depends(get_erp_gateway),
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
) -> StreamingResponse:
    token = authorization.removeprefix("Bearer ").strip()
    conv_id = uuid.UUID(body.conversation_id) if body.conversation_id else None
    conv = await get_or_create_conversation(session, user.external_id, conv_id)
    history = await load_history(session, conv.id)
    ctx = ToolContext(token=token, erp=erp, user_external_id=user.external_id)

    run = await orchestrator.run(body.message, history=history, role=Role(user.role), ctx=ctx)
    model = get_profile("chat").model

    await append_message(session, conv.id, "user", body.message)
    await append_message(session, conv.id, "assistant", run.text)
    await record(
        session,
        user_external_id=user.external_id,
        action="chat_query",
        tool="agente.chat",
        params={"model": model, "tools_used": run.tools_used, "conversation_id": str(conv.id)},
        result_summary=run.text[:200],
    )

    async def event_stream() -> AsyncIterator[bytes]:
        meta = {"type": "meta", "conversation_id": str(conv.id), "model": model,
                "tools_used": run.tools_used}
        yield f"data: {json.dumps(meta)}\n\n".encode()
        for piece in _chunk(run.text):
            yield f"data: {json.dumps({'type': 'token', 'text': piece})}\n\n".encode()
        yield f"data: {json.dumps({'type': 'done'})}\n\n".encode()

    return StreamingResponse(event_stream(), media_type="text/event-stream")
