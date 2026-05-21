from pydantic import BaseModel


class TenantSummary(BaseModel):
    practitioner_count: int
    deal_count: int
    wallet_pass_count: int
