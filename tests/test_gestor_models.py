from app.gestor.models import Project, Task

def test_project_columns():
    cols = set(Project.__table__.columns.keys())
    assert {"id", "user_external_id", "name", "created_at"} <= cols

def test_task_columns():
    cols = set(Task.__table__.columns.keys())
    assert {"id", "project_id", "title", "task_type", "status",
            "assignee", "due_date", "position", "created_at"} <= cols
