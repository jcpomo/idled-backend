import pytest
from app.documentos.service import create_document, get_document, set_status, list_documents

@pytest.mark.asyncio
async def test_create_and_get(session):
    doc = await create_document(session, "ext-1", "f.pdf", "application/pdf", "k/1")
    assert doc.status == "uploaded"
    again = await get_document(session, doc.id)
    assert again.filename == "f.pdf"

@pytest.mark.asyncio
async def test_set_status_and_list(session):
    d1 = await create_document(session, "ext-1", "a.pdf", "application/pdf", "k/a")
    await create_document(session, "ext-1", "b.xlsx", "application/vnd.ms-excel", "k/b")
    await create_document(session, "ext-2", "c.pdf", "application/pdf", "k/c")
    await set_status(session, d1.id, "indexed")
    refreshed = await get_document(session, d1.id)
    assert refreshed.status == "indexed"
    mine = await list_documents(session, "ext-1")
    assert {d.filename for d in mine} == {"a.pdf", "b.xlsx"}  # not ext-2's
