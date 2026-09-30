from datetime import datetime
from decimal import Decimal
from uuid import uuid4
from typing import Literal
from pydantic import BaseModel, Field

from app.models.conversation import utc_now
from app.models.enums import (
    Currency,
    Exchange,
    MarketDataStatus,
)


class Stock(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid4())
    )
    symbol: str
    company_name: str
    exchange: Exchange
    currency: Currency = Currency.INR
    sector: str
    industry: str
    isin: str | None = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class MarketQuote(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid4())
    )
    symbol: str
    exchange: Exchange
    currency: Currency

    price: Decimal
    previous_close: Decimal
    change: Decimal
    change_percent: Decimal

    open: Decimal
    day_high: Decimal
    day_low: Decimal
    volume: int

    as_of: datetime
    data_status: MarketDataStatus
    provider: str

    received_at: datetime = Field(default_factory=utc_now)

class PriceCandle(BaseModel):
    id: str
    symbol: str
    exchange: Exchange
    currency: Currency

    interval: Literal["1d"] = "1d"
    timestamp: datetime

    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    previous_close: Decimal | None = None
    return_percent: Decimal | None = None

    volume: int

    data_status: MarketDataStatus
    provider: str

class PriceHistoryResponse(BaseModel):
    symbol: str
    exchange: Exchange
    currency: Currency
    interval: Literal["1d"]
    provider: str
    data_status: MarketDataStatus
    count: int
    candles: list[PriceCandle]

class FinancialStatement(BaseModel):
    id: str
    symbol: str
    exchange: Exchange

    fiscal_year: str
    currency: Currency = Currency.INR
    unit: Literal["INR_CRORE"] = "INR_CRORE"

    revenue: Decimal
    ebitda: Decimal
    ebit: Decimal
    net_income: Decimal

    total_assets: Decimal
    shareholder_equity: Decimal
    total_debt: Decimal
    current_assets: Decimal
    current_liabilities: Decimal
    shares_outstanding: Decimal

    data_status: MarketDataStatus
    provider: str
    reported_at: datetime


class FundamentalRatios(BaseModel):
    symbol: str
    fiscal_year: str
    currency: Currency

    earnings_per_share: Decimal
    book_value_per_share: Decimal

    price_to_earnings: Decimal
    price_to_book: Decimal

    return_on_equity_percent: Decimal
    return_on_capital_employed_percent: Decimal
    net_profit_margin_percent: Decimal
    revenue_growth_percent: Decimal | None

    debt_to_equity: Decimal
    current_ratio: Decimal


class FundamentalsResponse(BaseModel):
    symbol: str
    exchange: Exchange
    data_status: MarketDataStatus
    provider: str

    latest_statement: FinancialStatement
    previous_statement: FinancialStatement | None
    ratios: FundamentalRatios