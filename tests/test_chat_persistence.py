import pytest
from app.agente.service import get_or_create_conversation, append_message, load_history

@pytest.mark.asyncio
async def test_conversation_and_history_roundtrip(session):
    conv = await get_or_create_conversation(session, "ext-1", None)
    await append_message(session, conv.id, "user", "hola")
    await append_message(session, conv.id, "assistant", "buenas")
    await append_message(session, conv.id, "tool", "no debe aparecer en history")
    history = await load_history(session, conv.id)
    assert [m.role for m in history] == ["user", "assistant"]
    assert history[0].content == "hola"

@pytest.mark.asyncio
async def test_get_or_create_existing(session):
    conv = await get_or_create_conversation(session, "ext-1", None)
    same = await get_or_create_conversation(session, "ext-1", conv.id)
    assert same.id == conv.id

@pytest.mark.asyncio
async def test_conversation_is_scoped_to_owner(session):
    # user A creates a conversation
    conv_a = await get_or_create_conversation(session, "user-A", None)
    # user B passes user A's conversation_id -> must NOT get A's conversation; gets a new one owned by B
    conv_b = await get_or_create_conversation(session, "user-B", conv_a.id)
    assert conv_b.id != conv_a.id
    assert conv_b.user_external_id == "user-B"
