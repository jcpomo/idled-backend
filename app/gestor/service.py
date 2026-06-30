import uuid
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.gestor.models import Project, Task

async def create_project(session: AsyncSession, user_external_id: str, name: str) -> Project:
    project = Project(user_external_id=user_external_id, name=name)
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project

async def list_projects(session: AsyncSession, user_external_id: str) -> list[Project]:
    result = await session.execute(
        select(Project).where(Project.user_external_id == user_external_id)
        .order_by(Project.created_at.desc())
    )
    return list(result.scalars().all())

async def get_owned_project(
    session: AsyncSession, project_id: uuid.UUID, user_external_id: str
) -> Project | None:
    result = await session.execute(
        select(Project).where(
            Project.id == project_id, Project.user_external_id == user_external_id
        )
    )
    return result.scalar_one_or_none()

async def rename_project(
    session: AsyncSession, project_id: uuid.UUID, user_external_id: str, name: str
) -> Project | None:
    project = await get_owned_project(session, project_id, user_external_id)
    if project is None:
        return None
    project.name = name
    await session.commit()
    await session.refresh(project)
    return project

async def delete_project(
    session: AsyncSession, project_id: uuid.UUID, user_external_id: str
) -> bool:
    project = await get_owned_project(session, project_id, user_external_id)
    if project is None:
        return False
    await session.execute(delete(Task).where(Task.project_id == project_id))
    await session.delete(project)
    await session.commit()
    return True
