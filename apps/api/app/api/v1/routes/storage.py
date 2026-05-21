from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_principal
from app.auth.types import AuthPrincipal
from app.schemas.storage import PresignUploadRequest, PresignUploadResponse
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
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return PresignUploadResponse(
        object_key=presigned.object_key,
        upload_url=presigned.upload_url,
        content_type=presigned.content_type,
        expires_in=presigned.expires_in,
    )
