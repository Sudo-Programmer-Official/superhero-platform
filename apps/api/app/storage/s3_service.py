from __future__ import annotations

import uuid
from dataclasses import dataclass

import boto3

from app.config import settings

_ALLOWED_FOLDERS = {"practitioners", "deals", "wallet-assets", "branding", "temp"}
_FOLDER_POLICY = {
    "practitioners": {
        "mime_prefixes": ["image/"],
        "max_bytes": 8 * 1024 * 1024,
    },
    "deals": {
        "mime_prefixes": ["image/"],
        "max_bytes": 10 * 1024 * 1024,
    },
    "wallet-assets": {
        "mime_prefixes": ["image/", "application/pdf"],
        "max_bytes": 5 * 1024 * 1024,
    },
    "branding": {
        "mime_prefixes": ["image/"],
        "max_bytes": 8 * 1024 * 1024,
    },
    "temp": {
        "mime_prefixes": ["image/", "application/pdf"],
        "max_bytes": 10 * 1024 * 1024,
    },
}


@dataclass
class PresignedUpload:
    object_key: str
    upload_url: str
    content_type: str
    expires_in: int
    max_content_length: int


class S3StorageService:
    def __init__(self) -> None:
        self.bucket = settings.s3_bucket
        self.prefix = settings.s3_prefix.strip("/")
        self.region = settings.aws_region
        self._client = boto3.client("s3", region_name=self.region)

    def _safe_ext(self, filename: str) -> str:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
        return ext if ext.isalnum() else "bin"

    def _is_mime_allowed(self, folder: str, content_type: str) -> bool:
        allowed_prefixes = _FOLDER_POLICY[folder]["mime_prefixes"]
        return any(content_type.startswith(prefix) for prefix in allowed_prefixes)

    def build_object_key(self, folder: str, owner_id: str, filename: str) -> str:
        if folder not in _ALLOWED_FOLDERS:
            raise ValueError("Invalid folder")
        ext = self._safe_ext(filename)
        token = uuid.uuid4().hex
        return f"{self.prefix}/{folder}/{owner_id}/{token}.{ext}"

    def validate_upload_request(self, *, folder: str, content_type: str, content_length: int) -> int:
        if folder not in _ALLOWED_FOLDERS:
            raise ValueError("Invalid folder")
        if not self._is_mime_allowed(folder, content_type):
            raise ValueError("Content type not allowed for folder")
        max_bytes = _FOLDER_POLICY[folder]["max_bytes"]
        if content_length > max_bytes:
            raise ValueError(f"File too large for folder; max is {max_bytes} bytes")
        return int(max_bytes)

    def validate_object_key_prefix(self, object_key: str) -> None:
        if not object_key.startswith(f"{self.prefix}/"):
            raise ValueError("Object key is outside project prefix")

    def create_presigned_upload(
        self, *, folder: str, owner_id: str, filename: str, content_type: str, content_length: int
    ) -> PresignedUpload:
        max_bytes = self.validate_upload_request(
            folder=folder,
            content_type=content_type,
            content_length=content_length,
        )
        object_key = self.build_object_key(folder=folder, owner_id=owner_id, filename=filename)
        upload_url = self._client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": self.bucket,
                "Key": object_key,
                "ContentType": content_type,
                "ServerSideEncryption": "AES256",
            },
            ExpiresIn=settings.s3_presign_expires_seconds,
        )
        return PresignedUpload(
            object_key=object_key,
            upload_url=upload_url,
            content_type=content_type,
            expires_in=settings.s3_presign_expires_seconds,
            max_content_length=max_bytes,
        )
