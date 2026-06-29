import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.agente.models import AiConversation, AiMessage
from app.agente.provider import LLMMessage

async def get_or_create_conversation(
    session: AsyncSession, user_external_id: str, conversation_id: uuid.UUID | None
) -> AiConversation:
    if conversation_id is not None:
        result = await session.execute(
            select(AiConversation).where(
                AiConversation.id == conversation_id,
                AiConversation.user_external_id == user_external_id,
            )
        )
        existing = result.scalar_one_or_none()
        if existing is not None:
            return existing
    conv = AiConversation(user_external_id=user_external_id)
    session.add(conv)
    await session.commit()
    await session.refresh(conv)
    return conv

async def append_message(
    session: AsyncSession, conversation_id: uuid.UUID, role: str, content: str
) -> AiMessage:
    msg = AiMessage(conversation_id=conversation_id, role=role, content=content)
    session.add(msg)
    await session.commit()
    await session.refresh(msg)
    return msg

async def load_history(session: AsyncSession, conversation_id: uuid.UUID) -> list[LLMMessage]:
    result = await session.execute(
        select(AiMessage)
        .where(AiMessage.conversation_id == conversation_id)
        .order_by(AiMessage.created_at)
    )
    rows = result.scalars().all()
    return [
        LLMMessage(role=r.role, content=r.content)
        for r in rows
        if r.role in ("user", "assistant")
    ]
