from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from botocore.exceptions import ClientError

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_principal
from app.auth.types import AuthPrincipal
from app.db import get_db_session
from app.schemas.storage import (
    FinalizeAssetRequest,
    FinalizeAssetResponse,
    PresignUploadRequest,
    PresignUploadResponse,
)
from app.services.storage_service import StorageService
from app.storage.s3_service import S3StorageService
from app.repositories.practitioner_repository import PractitionerRepository

router = APIRouter(prefix="/storage", tags=["storage"])


@router.post("/presign-upload", response_model=PresignUploadResponse)
async def presign_upload(
    payload: PresignUploadRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
):
    if principal.role not in {"super_admin", "admin", "practitioner"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")

    try:
        presigned = S3StorageService().create_presigned_upload(
            folder=payload.folder,
            owner_id=principal.uid,
            filename=payload.filename,
            content_type=payload.content_type,
            content_length=payload.content_length,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return PresignUploadResponse(
        object_key=presigned.object_key,
        upload_url=presigned.upload_url,
        content_type=presigned.content_type,
        expires_in=presigned.expires_in,
        max_content_length=presigned.max_content_length,
    )


@router.post("/finalize-asset", response_model=FinalizeAssetResponse)
async def finalize_asset(
    payload: FinalizeAssetRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_db_session),
):
    if principal.role not in {"super_admin", "admin", "practitioner"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")

    target_id = await StorageService(session).finalize_asset(payload, principal)
    return FinalizeAssetResponse(
        target_type=payload.target_type,
        target_id=target_id,
        field_name=payload.field_name,
        object_key=payload.object_key,
    )


@router.post("/upload-practitioner-image")
async def upload_practitioner_image(
    practitioner_id: UUID = Form(...),
    file: UploadFile = File(...),
    principal: AuthPrincipal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_db_session),
):
    if principal.role not in {"super_admin", "admin", "practitioner"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")

    practitioner_repo = PractitionerRepository(session)
    practitioner = await practitioner_repo.get(practitioner_id)
    if not practitioner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Practitioner not found")
    if principal.role == "practitioner" and practitioner.firebase_uid != principal.uid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot modify this practitioner")

    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing filename")
    content_type = file.content_type or "application/octet-stream"

    body = await file.read()
    storage = S3StorageService()
    try:
        storage.validate_upload_request(
            folder="practitioners",
            content_type=content_type,
            content_length=len(body),
        )
        object_key = storage.build_object_key(
            folder="practitioners",
            owner_id=principal.uid,
            filename=file.filename,
        )
        storage.upload_bytes(object_key=object_key, body=body, content_type=content_type)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Storage upload failed: AWS credentials do not allow s3:PutObject "
                f"for bucket '{storage.bucket}' and prefix '{storage.prefix}/practitioners/'."
            ),
        ) from exc

    practitioner.profile_image = object_key
    await session.commit()
    await session.refresh(practitioner)

    return {
        "object_key": object_key,
        "avatar_url": practitioner.avatar_url,
        "profile_image": practitioner.profile_image,
    }
