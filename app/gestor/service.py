import uuid
from sqlalchemy import delete, func as safunc, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.gestor.models import Project, Task
from app.gestor.statuses import is_valid_status

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

async def create_task(
    session: AsyncSession, project_id: uuid.UUID, user_external_id: str, *,
    title: str, task_type: str = "PPTO", status: str = "open",
    assignee: str | None = None, due_date: str | None = None,
) -> Task | None:
    if not is_valid_status(status):
        raise ValueError(f"Estado inválido: {status}")
    project = await get_owned_project(session, project_id, user_external_id)
    if project is None:
        return None
    result = await session.execute(
        select(safunc.max(Task.position)).where(
            Task.project_id == project_id, Task.status == status
        )
    )
    max_pos = result.scalar()
    position = 0 if max_pos is None else max_pos + 1
    task = Task(
        project_id=project_id, title=title, task_type=task_type, status=status,
        assignee=assignee, due_date=due_date, position=position,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task

async def list_tasks(
    session: AsyncSession, project_id: uuid.UUID, user_external_id: str
) -> list[Task] | None:
    project = await get_owned_project(session, project_id, user_external_id)
    if project is None:
        return None
    result = await session.execute(
        select(Task).where(Task.project_id == project_id)
        .order_by(Task.status, Task.position)
    )
    return list(result.scalars().all())

async def get_owned_task(
    session: AsyncSession, task_id: uuid.UUID, user_external_id: str
) -> Task | None:
    result = await session.execute(
        select(Task).join(Project, Task.project_id == Project.id).where(
            Task.id == task_id, Project.user_external_id == user_external_id
        )
    )
    return result.scalar_one_or_none()

async def update_task(
    session: AsyncSession, task_id: uuid.UUID, user_external_id: str, *,
    title: str | None = None, task_type: str | None = None,
    assignee: str | None = None, due_date: str | None = None,
) -> Task | None:
    task = await get_owned_task(session, task_id, user_external_id)
    if task is None:
        return None
    if title is not None:
        task.title = title
    if task_type is not None:
        task.task_type = task_type
    if assignee is not None:
        task.assignee = assignee
    if due_date is not None:
        task.due_date = due_date
    await session.commit()
    await session.refresh(task)
    return task

async def delete_task(
    session: AsyncSession, task_id: uuid.UUID, user_external_id: str
) -> bool:
    task = await get_owned_task(session, task_id, user_external_id)
    if task is None:
        return False
    await session.delete(task)
    await session.commit()
    return True

async def _renumber(session: AsyncSession, project_id: uuid.UUID, status: str) -> None:
    result = await session.execute(
        select(Task).where(Task.project_id == project_id, Task.status == status)
        .order_by(Task.position, Task.created_at)
    )
    for index, task in enumerate(result.scalars().all()):
        task.position = index

async def move_task(
    session: AsyncSession, task_id: uuid.UUID, user_external_id: str, *,
    status: str, position: int,
) -> Task | None:
    if not is_valid_status(status):
        raise ValueError(f"Estado inválido: {status}")
    task = await get_owned_task(session, task_id, user_external_id)
    if task is None:
        return None
    old_status = task.status
    task.status = status
    # Flush so the DB reflects the new status: the target-column query below then
    # includes the moved task (filtered out by id), and the old-column renumber excludes it.
    await session.flush()
    # Rebuild the target column with the moved task inserted at `position`.
    result = await session.execute(
        select(Task).where(Task.project_id == task.project_id, Task.status == status)
        .order_by(Task.position, Task.created_at)
    )
    others = [t for t in result.scalars().all() if t.id != task.id]
    reordered = others[:position] + [task] + others[position:]
    for index, t in enumerate(reordered):
        t.position = index
    # If it changed columns, renumber the source column to close the gap.
    if old_status != status:
        await _renumber(session, task.project_id, old_status)
    await session.commit()
    await session.refresh(task)
    return task
