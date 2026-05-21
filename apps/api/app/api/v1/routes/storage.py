from fastapi import APIRouter, Depends, HTTPException, status

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
