import logging
from pathlib import Path
from typing import BinaryIO, Optional

from config import (
    UPLOAD_DIR,
    S3_BUCKET,
    S3_REGION,
    S3_ENDPOINT,
    S3_ACL,
)
from storage_helpers import resolve_collision_path

try:
    import boto3
    from botocore.exceptions import ClientError
except Exception:
    boto3 = None


log = logging.getLogger(__name__)


class LocalStorage:
    def __init__(self, base_dir: str = UPLOAD_DIR):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _dest_path(
        self,
        filename: str,
        prefix: Optional[str] = "",
    ) -> Path:
        if prefix:
            return self.base_dir.joinpath(prefix, filename)

        return self.base_dir.joinpath(filename)

    def save_with_collision_resolution(
        self,
        file_stream: BinaryIO,
        filename: str,
        prefix: Optional[str] = "",
    ) -> str:
        dest = self._dest_path(filename, prefix)
        dest.parent.mkdir(parents=True, exist_ok=True)

        real_dest = resolve_collision_path(dest)

        file_stream.seek(0)

        with open(real_dest, "wb") as f:
            for chunk in iter(lambda: file_stream.read(8192), b""):
                f.write(chunk)

        return str(real_dest)


class S3Storage:
    def __init__(
        self,
        bucket: str = S3_BUCKET,
        region: str = S3_REGION,
        endpoint: str = S3_ENDPOINT,
    ):
        if boto3 is None:
            raise RuntimeError(
                "boto3 is required for S3 storage"
            )

        self.bucket = bucket

        self.s3 = boto3.client(
            "s3",
            region_name=region,
            endpoint_url=endpoint or None,
        )

    def _exists(self, key: str) -> bool:
        try:
            self.s3.head_object(
                Bucket=self.bucket,
                Key=key,
            )
            return True

        except ClientError:
            return False

    def _resolve_key(self, key: str) -> str:
        if not self._exists(key):
            return key

        base, dot, ext = key.rpartition(".")

        if dot:
            stem = base
            suffix = "." + ext
        else:
            stem = key
            suffix = ""

        counter = 1

        while True:
            candidate = f"{stem} ({counter}){suffix}"

            if not self._exists(candidate):
                return candidate

            counter += 1

    def save_with_collision_resolution(
        self,
        file_stream: BinaryIO,
        key: str,
        prefix: Optional[str] = "",
    ) -> str:
        if prefix:
            key = f"{prefix.rstrip('/')}/{key}"

        key = self._resolve_key(key)

        file_stream.seek(0)

        self.s3.upload_fileobj(
            file_stream,
            self.bucket,
            key,
            ExtraArgs={
                "ACL": S3_ACL,
            },
        )

        return f"s3://{self.bucket}/{key}"