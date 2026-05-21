from __future__ import annotations

import mimetypes
import uuid
from dataclasses import dataclass

import boto3

from app.config import settings

_ALLOWED_FOLDERS = {"practitioners", "deals", "wallet-assets", "branding", "temp"}


@dataclass
class PresignedUpload:
    object_key: str
    upload_url: str
    content_type: str
    expires_in: int


class S3StorageService:
    def __init__(self) -> None:
        self.bucket = settings.s3_bucket
        self.prefix = settings.s3_prefix.strip("/")
        self.region = settings.aws_region
        self._client = boto3.client("s3", region_name=self.region)

    def _safe_ext(self, filename: str) -> str:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
        return ext if ext.isalnum() else "bin"

    def _infer_content_type(self, filename: str) -> str:
        guessed, _ = mimetypes.guess_type(filename)
        return guessed or "application/octet-stream"

    def build_object_key(self, folder: str, owner_id: str, filename: str) -> str:
        if folder not in _ALLOWED_FOLDERS:
            raise ValueError("Invalid folder")
        ext = self._safe_ext(filename)
        token = uuid.uuid4().hex
        return f"{self.prefix}/{folder}/{owner_id}/{token}.{ext}"

    def create_presigned_upload(self, *, folder: str, owner_id: str, filename: str) -> PresignedUpload:
        object_key = self.build_object_key(folder=folder, owner_id=owner_id, filename=filename)
        content_type = self._infer_content_type(filename)
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
        )
