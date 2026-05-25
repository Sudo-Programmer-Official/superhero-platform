from datetime import datetime

from pydantic import BaseModel


class DashboardMetricSummary(BaseModel):
    total_bookings: int
    revenue: float
    redemptions: int
    conversion_rate: float


class DashboardUpcomingItem(BaseModel):
    id: str
    title: str
    image: str | None
    starts_at: datetime
    location: str
    seats_sold: int
    capacity: int


class DashboardSummaryResponse(BaseModel):
    metrics: DashboardMetricSummary
    upcoming: list[DashboardUpcomingItem]

