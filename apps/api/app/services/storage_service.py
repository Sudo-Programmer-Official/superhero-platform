from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.types import AuthPrincipal
from app.repositories.deal_card_repository import DealCardRepository
from app.repositories.practitioner_repository import PractitionerRepository
from app.schemas.storage import FinalizeAssetRequest
from app.storage.s3_service import S3StorageService


class StorageService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.practitioner_repo = PractitionerRepository(session)
        self.deal_repo = DealCardRepository(session)
        self.storage = S3StorageService()

    def _assert_project_key(self, object_key: str) -> None:
        try:
            self.storage.validate_object_key_prefix(object_key)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    async def finalize_asset(self, payload: FinalizeAssetRequest, principal: AuthPrincipal) -> UUID:
        self._assert_project_key(payload.object_key)

        if payload.target_type == "practitioner":
            if payload.field_name != "profile_image":
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid field for practitioner")
            practitioner = await self.practitioner_repo.get(payload.target_id)
            if not practitioner:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Practitioner not found")
            if principal.role == "practitioner" and practitioner.firebase_uid != principal.uid:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot modify this practitioner")
            practitioner.profile_image = payload.object_key
            await self.session.commit()
            return practitioner.id

        if payload.target_type == "deal_card":
            if payload.field_name != "image":
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid field for deal card")
            deal = await self.deal_repo.get(payload.target_id)
            if not deal:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal card not found")
            if principal.role == "practitioner":
                practitioner = await self.practitioner_repo.get(deal.practitioner_id)
                if not practitioner or practitioner.firebase_uid != principal.uid:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot modify this deal")
            deal.image = payload.object_key
            await self.session.commit()
            return deal.id

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported target type")
