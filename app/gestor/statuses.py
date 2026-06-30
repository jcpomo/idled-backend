TASK_STATUSES: list[str] = ["open", "progress", "review", "done"]

def is_valid_status(status: str) -> bool:
    return status in TASK_STATUSES
