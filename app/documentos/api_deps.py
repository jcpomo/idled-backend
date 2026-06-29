from app.documentos.deps import enqueue_index_job, get_storage
from app.documentos.storage import ObjectStorage

def get_storage_dep() -> ObjectStorage:
    return get_storage()

def enqueue_dep():
    return enqueue_index_job
