from app.gestor.statuses import TASK_STATUSES, is_valid_status

def test_statuses_are_the_design_columns():
    assert TASK_STATUSES == ["open", "progress", "review", "done"]

def test_is_valid_status():
    assert is_valid_status("open")
    assert is_valid_status("done")
    assert not is_valid_status("todo")
    assert not is_valid_status("")
