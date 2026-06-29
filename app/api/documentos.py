import uuid
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.audit.service import record
from app.auth.dependencies import get_current_user, require_permission
from app.auth.models import User
from app.core.db import get_session
from app.documentos.api_deps import enqueue_dep, get_storage_dep
from app.documentos.service import create_document, list_documents
from app.documentos.storage import ObjectStorage

router = APIRouter(prefix="/api/documentos", tags=["documentos"])

@router.post("", dependencies=[Depends(require_permission("documentos:write"))])
async def upload(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    storage: ObjectStorage = Depends(get_storage_dep),
    enqueue=Depends(enqueue_dep),
) -> dict:
    data = await file.read()
    storage_key = f"{user.external_id}/{uuid.uuid4()}/{file.filename}"
    storage.put(storage_key, data, file.content_type or "application/octet-stream")
    doc = await create_document(
        session, user.external_id, file.filename or "sin-nombre",
        file.content_type or "application/octet-stream", storage_key,
    )
    await enqueue(doc.id)
    await record(
        session, user_external_id=user.external_id, action="document_upload",
        tool="documentos.upload", params={"document_id": str(doc.id), "filename": doc.filename},
        result_summary=f"subido {doc.filename}",
    )
    return {"document_id": str(doc.id), "status": doc.status}

@router.get("", dependencies=[Depends(require_permission("documentos:read"))])
async def listar(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    docs = await list_documents(session, user.external_id)
    return [
        {"id": str(d.id), "filename": d.filename, "status": d.status,
         "created_at": d.created_at.isoformat() if d.created_at else None}
        for d in docs
    ]
