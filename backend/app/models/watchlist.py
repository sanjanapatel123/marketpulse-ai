from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from pydantic import BaseModel, Field

from app.models.conversation import utc_now
from app.models.enums import (
    Currency,
    Exchange,
    PriceAlertCondition,
    PriceAlertStatus,
)


class Watchlist(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid4())
    )
    name: str
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class WatchlistItem(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid4())
    )
    watchlist_id: str
    symbol: str
    exchange: Exchange = Exchange.NSE
    added_at: datetime = Field(default_factory=utc_now)


class PriceAlert(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid4())
    )
    watchlist_id: str
    symbol: str
    exchange: Exchange = Exchange.NSE
    currency: Currency = Currency.INR

    condition: PriceAlertCondition
    threshold: Decimal
    status: PriceAlertStatus = (
        PriceAlertStatus.ACTIVE
    )

    triggered_price: Decimal | None = None
    triggered_at: datetime | None = None

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class CreateWatchlistRequest(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
    )


class AddWatchlistItemRequest(BaseModel):
    symbol: str = Field(
        min_length=1,
        max_length=20,
    )


class CreatePriceAlertRequest(BaseModel):
    symbol: str = Field(
        min_length=1,
        max_length=20,
    )
    condition: PriceAlertCondition
    threshold: Decimal = Field(gt=0)


class WatchlistItemQuote(BaseModel):
    item: WatchlistItem
    company_name: str
    sector: str
    price: Decimal
    change: Decimal
    change_percent: Decimal
    currency: Currency
    data_status: str


class WatchlistDetailResponse(BaseModel):
    watchlist: Watchlist
    items: list[WatchlistItemQuote]
    alerts: list[PriceAlert]

class AlertEvaluationResult(BaseModel):
    evaluated_count: int
    triggered_count: int
    triggered_alerts: list[PriceAlert]
    evaluated_at: datetime