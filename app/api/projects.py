import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.core.db import get_session
from app.gestor.service import (
    create_project, list_projects, rename_project, delete_project,
    create_task, list_tasks,
)
from app.gestor.statuses import is_valid_status

router = APIRouter(prefix="/api/projects", tags=["gestor"])

class ProjectBody(BaseModel):
    name: str

class TaskBody(BaseModel):
    title: str
    task_type: str = "PPTO"
    status: str = "open"
    assignee: str | None = None
    due_date: str | None = None

def _task_dict(t) -> dict:
    return {"id": str(t.id), "title": t.title, "task_type": t.task_type,
            "status": t.status, "assignee": t.assignee, "due_date": t.due_date,
            "position": t.position}

@router.post("")
async def create(body: ProjectBody, user: User = Depends(get_current_user),
                 session: AsyncSession = Depends(get_session)) -> dict:
    p = await create_project(session, user.external_id, body.name)
    return {"id": str(p.id), "name": p.name}

@router.get("")
async def listar(user: User = Depends(get_current_user),
                 session: AsyncSession = Depends(get_session)) -> list[dict]:
    projects = await list_projects(session, user.external_id)
    return [{"id": str(p.id), "name": p.name,
             "created_at": p.created_at.isoformat() if p.created_at else None}
            for p in projects]

@router.patch("/{project_id}")
async def rename(project_id: uuid.UUID, body: ProjectBody,
                 user: User = Depends(get_current_user),
                 session: AsyncSession = Depends(get_session)) -> dict:
    p = await rename_project(session, project_id, user.external_id, body.name)
    if p is None:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return {"id": str(p.id), "name": p.name}

@router.delete("/{project_id}")
async def borrar(project_id: uuid.UUID, user: User = Depends(get_current_user),
                 session: AsyncSession = Depends(get_session)) -> dict:
    ok = await delete_project(session, project_id, user.external_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return {"deleted": True}

@router.post("/{project_id}/tasks")
async def crear_tarea(project_id: uuid.UUID, body: TaskBody,
                      user: User = Depends(get_current_user),
                      session: AsyncSession = Depends(get_session)) -> dict:
    if not is_valid_status(body.status):
        raise HTTPException(status_code=422, detail=f"Estado inválido: {body.status}")
    t = await create_task(
        session, project_id, user.external_id, title=body.title, task_type=body.task_type,
        status=body.status, assignee=body.assignee, due_date=body.due_date,
    )
    if t is None:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return _task_dict(t)

@router.get("/{project_id}/tasks")
async def listar_tareas(project_id: uuid.UUID, user: User = Depends(get_current_user),
                        session: AsyncSession = Depends(get_session)) -> list[dict]:
    tasks = await list_tasks(session, project_id, user.external_id)
    if tasks is None:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return [_task_dict(t) for t in tasks]
