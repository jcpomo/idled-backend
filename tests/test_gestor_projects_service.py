import pytest
from app.gestor.service import (
    create_project, list_projects, get_owned_project, rename_project, delete_project,
)

@pytest.mark.asyncio
async def test_create_list_owned(session):
    p = await create_project(session, "ext-1", "Serie X")
    assert p.name == "Serie X"
    mine = await list_projects(session, "ext-1")
    assert [x.name for x in mine] == ["Serie X"]
    # other user sees nothing and cannot fetch it
    assert await list_projects(session, "ext-2") == []
    assert await get_owned_project(session, p.id, "ext-2") is None
    assert await get_owned_project(session, p.id, "ext-1") is not None

@pytest.mark.asyncio
async def test_rename_and_delete_owner_only(session):
    p = await create_project(session, "ext-1", "A")
    assert await rename_project(session, p.id, "ext-2", "Hacked") is None  # not owner
    renamed = await rename_project(session, p.id, "ext-1", "B")
    assert renamed.name == "B"
    assert await delete_project(session, p.id, "ext-2") is False  # not owner
    assert await delete_project(session, p.id, "ext-1") is True
    assert await get_owned_project(session, p.id, "ext-1") is None
