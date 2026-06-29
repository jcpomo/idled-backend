from typing import Protocol
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

class ObjectStorage(Protocol):
    def put(self, key: str, data: bytes, content_type: str) -> None: ...
    def get(self, key: str) -> bytes: ...

class FakeStorage:
    def __init__(self) -> None:
        self._data: dict[str, bytes] = {}

    def put(self, key: str, data: bytes, content_type: str) -> None:
        self._data[key] = data

    def get(self, key: str) -> bytes:
        return self._data[key]

class S3Storage:
    def __init__(self, endpoint: str, access_key: str, secret_key: str, bucket: str):
        self._bucket = bucket
        self._client = boto3.client(
            "s3", endpoint_url=endpoint,
            aws_access_key_id=access_key, aws_secret_access_key=secret_key,
            config=Config(signature_version="s3v4"), region_name="us-east-1",
        )

    def ensure_bucket(self) -> None:
        try:
            self._client.head_bucket(Bucket=self._bucket)
        except ClientError:
            self._client.create_bucket(Bucket=self._bucket)

    def put(self, key: str, data: bytes, content_type: str) -> None:
        self._client.put_object(Bucket=self._bucket, Key=key, Body=data, ContentType=content_type)

    def get(self, key: str) -> bytes:
        resp = self._client.get_object(Bucket=self._bucket, Key=key)
        return resp["Body"].read()
