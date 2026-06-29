import os
import uuid
import pytest
from app.documentos.storage import S3Storage, FakeStorage

def test_fake_storage_roundtrip():
    st = FakeStorage()
    st.put("k/1", b"hello", "text/plain")
    assert st.get("k/1") == b"hello"

@pytest.mark.integration
def test_s3_storage_roundtrip_against_minio():
    st = S3Storage(
        endpoint=os.getenv("MINIO_ENDPOINT", "http://minio:9000"),
        access_key="minio", secret_key="minio12345", bucket="documents-test",
    )
    st.ensure_bucket()
    key = f"test/{uuid.uuid4()}.txt"
    st.put(key, b"contenido", "text/plain")
    assert st.get(key) == b"contenido"
