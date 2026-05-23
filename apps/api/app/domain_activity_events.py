from dataclasses import dataclass


class ActivityEventType:
    DEAL_CREATED = "deal.created"
    DEAL_PUBLISHED = "deal.published"
    DEAL_ARCHIVED = "deal.archived"
    DEAL_DUPLICATED = "deal.duplicated"

    BOOKING_CREATED = "booking.created"
    BOOKING_PAID = "booking.paid"
    BOOKING_REFUNDED = "booking.refunded"

    WALLET_GENERATED = "wallet.generated"
    WALLET_REDEEMED = "wallet.redeemed"

    REDEMPTION_SUCCESS = "redemption.success"
    REDEMPTION_FAILED = "redemption.failed"


@dataclass(frozen=True)
class EventScope:
    tenant_id: str
    practitioner_id: str | None
    actor_id: str | None


def default_tenant() -> str:
    return "default"
