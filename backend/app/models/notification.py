from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class NotificationEventType(str, Enum):
    PRICE_ALERT_TRIGGERED = "price_alert_triggered"


class NotificationPayload(BaseModel):
    alert_id: str
    watchlist_id: str
    symbol: str
    exchange: str
    currency: str

    condition: str
    threshold: str
    triggered_price: str

    title: str
    message: str


class NotificationEvent(BaseModel):
    id: str

    # Server-owned global ordering position.
    # This is also used as the SSE resume cursor.
    sequence: int = Field(ge=1)

    type: NotificationEventType

    # Stable source identity prevents duplicate logical events.
    source_id: str
    source_type: str

    payload: NotificationPayload
    created_at: datetime


class NotificationHistoryResponse(BaseModel):
    events: list[NotificationEvent]
    count: int
    latest_cursor: int


class NotificationStreamError(BaseModel):
    code: str
    message: str
    recoverable: bool
    earliest_available_cursor: int | None = None
    latest_available_cursor: int | None = None