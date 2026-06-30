import pytest
from app.gestor.service import create_project, create_task, list_tasks, move_task

async def _positions(session, project_id, status):
    tasks = await list_tasks(session, project_id, "ext-1")
    return [(t.title, t.position) for t in tasks if t.status == status]

@pytest.mark.asyncio
async def test_move_to_other_column_reorders_both(session):
    p = await create_project(session, "ext-1", "P")
    a = await create_task(session, p.id, "ext-1", title="a")  # open 0
    b = await create_task(session, p.id, "ext-1", title="b")  # open 1
    c = await create_task(session, p.id, "ext-1", title="c")  # open 2

    moved = await move_task(session, b.id, "ext-1", status="done", position=0)
    assert moved.status == "done" and moved.position == 0
    # source column 'open' renumbered without gaps: a=0, c=1
    assert await _positions(session, p.id, "open") == [("a", 0), ("c", 1)]
    # target column 'done': b=0
    assert await _positions(session, p.id, "done") == [("b", 0)]

@pytest.mark.asyncio
async def test_move_within_column_to_index(session):
    p = await create_project(session, "ext-1", "P")
    a = await create_task(session, p.id, "ext-1", title="a")  # 0
    b = await create_task(session, p.id, "ext-1", title="b")  # 1
    c = await create_task(session, p.id, "ext-1", title="c")  # 2
    # move c to index 0 within 'open' -> c,a,b
    await move_task(session, c.id, "ext-1", status="open", position=0)
    assert await _positions(session, p.id, "open") == [("c", 0), ("a", 1), ("b", 2)]

@pytest.mark.asyncio
async def test_move_owner_only_and_valid_status(session):
    p = await create_project(session, "ext-1", "P")
    t = await create_task(session, p.id, "ext-1", title="a")
    assert await move_task(session, t.id, "ext-2", status="done", position=0) is None
    with pytest.raises(ValueError):
        await move_task(session, t.id, "ext-1", status="nope", position=0)
