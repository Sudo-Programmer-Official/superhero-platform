from pydantic import BaseModel, Field


class PresignUploadRequest(BaseModel):
    folder: str = Field(pattern="^(practitioners|deals|wallet-assets|branding|temp)$")
    filename: str


class PresignUploadResponse(BaseModel):
    object_key: str
    upload_url: str
    content_type: str
    expires_in: int
