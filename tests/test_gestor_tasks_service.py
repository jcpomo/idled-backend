import pytest
from app.gestor.service import (
    create_project, create_task, list_tasks, get_owned_task, update_task, delete_task,
)

@pytest.mark.asyncio
async def test_create_and_list_owned(session):
    p = await create_project(session, "ext-1", "P")
    t1 = await create_task(session, p.id, "ext-1", title="A")
    t2 = await create_task(session, p.id, "ext-1", title="B", status="done")
    assert t1.status == "open" and t1.position == 0
    assert t2.status == "done"
    # other user cannot create or list
    assert await create_task(session, p.id, "ext-2", title="X") is None
    assert await list_tasks(session, p.id, "ext-2") is None
    mine = await list_tasks(session, p.id, "ext-1")
    assert {t.title for t in mine} == {"A", "B"}

@pytest.mark.asyncio
async def test_position_increments_within_status(session):
    p = await create_project(session, "ext-1", "P")
    a = await create_task(session, p.id, "ext-1", title="a")  # open pos 0
    b = await create_task(session, p.id, "ext-1", title="b")  # open pos 1
    assert (a.position, b.position) == (0, 1)

@pytest.mark.asyncio
async def test_invalid_status_raises(session):
    p = await create_project(session, "ext-1", "P")
    with pytest.raises(ValueError):
        await create_task(session, p.id, "ext-1", title="x", status="todo")

@pytest.mark.asyncio
async def test_update_and_delete_owner_only(session):
    p = await create_project(session, "ext-1", "P")
    t = await create_task(session, p.id, "ext-1", title="a")
    assert await update_task(session, t.id, "ext-2", title="hack") is None
    upd = await update_task(session, t.id, "ext-1", title="b", assignee="ED")
    assert upd.title == "b" and upd.assignee == "ED"
    assert await delete_task(session, t.id, "ext-2") is False
    assert await delete_task(session, t.id, "ext-1") is True
    assert await get_owned_task(session, t.id, "ext-1") is None
