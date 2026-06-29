import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.documentos.models import Document

async def create_document(
    session: AsyncSession, user_external_id: str, filename: str,
    content_type: str, storage_key: str,
) -> Document:
    doc = Document(
        user_external_id=user_external_id, filename=filename,
        content_type=content_type, storage_key=storage_key, status="uploaded",
    )
    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    return doc

async def get_document(session: AsyncSession, document_id: uuid.UUID) -> Document | None:
    result = await session.execute(select(Document).where(Document.id == document_id))
    return result.scalar_one_or_none()

async def set_status(
    session: AsyncSession, document_id: uuid.UUID, status: str, error: str | None = None
) -> None:
    doc = await get_document(session, document_id)
    if doc is not None:
        doc.status = status
        doc.error = error
        await session.commit()

async def list_documents(session: AsyncSession, user_external_id: str) -> list[Document]:
    result = await session.execute(
        select(Document)
        .where(Document.user_external_id == user_external_id)
        .order_by(Document.created_at.desc())
    )
    return list(result.scalars().all())
