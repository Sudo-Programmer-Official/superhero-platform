from uuid import UUID

from pydantic import BaseModel, Field


class PresignUploadRequest(BaseModel):
    folder: str = Field(pattern="^(practitioners|deals|wallet-assets|branding|temp)$")
    filename: str
    content_type: str
    content_length: int = Field(gt=0)


class PresignUploadResponse(BaseModel):
    object_key: str
    upload_url: str
    content_type: str
    expires_in: int
    max_content_length: int


class FinalizeAssetRequest(BaseModel):
    target_type: str = Field(pattern="^(practitioner|deal_card)$")
    target_id: UUID
    field_name: str = Field(pattern="^(profile_image|image)$")
    object_key: str


class FinalizeAssetResponse(BaseModel):
    target_type: str
    target_id: UUID
    field_name: str
    object_key: str
