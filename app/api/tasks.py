import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.core.db import get_session
from app.gestor.service import update_task, delete_task, move_task
from app.gestor.statuses import is_valid_status

router = APIRouter(prefix="/api/tasks", tags=["gestor"])

class TaskUpdateBody(BaseModel):
    title: str | None = None
    task_type: str | None = None
    assignee: str | None = None
    due_date: str | None = None

class MoveBody(BaseModel):
    status: str
    position: int

def _task_dict(t) -> dict:
    return {"id": str(t.id), "title": t.title, "task_type": t.task_type,
            "status": t.status, "assignee": t.assignee, "due_date": t.due_date,
            "position": t.position}

@router.patch("/{task_id}")
async def actualizar(task_id: uuid.UUID, body: TaskUpdateBody,
                     user: User = Depends(get_current_user),
                     session: AsyncSession = Depends(get_session)) -> dict:
    t = await update_task(session, task_id, user.external_id, title=body.title,
                          task_type=body.task_type, assignee=body.assignee, due_date=body.due_date)
    if t is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return _task_dict(t)

@router.delete("/{task_id}")
async def borrar(task_id: uuid.UUID, user: User = Depends(get_current_user),
                 session: AsyncSession = Depends(get_session)) -> dict:
    ok = await delete_task(session, task_id, user.external_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return {"deleted": True}

@router.post("/{task_id}/move")
async def mover(task_id: uuid.UUID, body: MoveBody,
                user: User = Depends(get_current_user),
                session: AsyncSession = Depends(get_session)) -> dict:
    if not is_valid_status(body.status):
        raise HTTPException(status_code=422, detail=f"Estado inválido: {body.status}")
    t = await move_task(session, task_id, user.external_id, status=body.status, position=body.position)
    if t is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return _task_dict(t)
