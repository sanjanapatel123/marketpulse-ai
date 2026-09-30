from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from pydantic import BaseModel, Field

from app.models.conversation import utc_now
from app.models.enums import (
    Currency,
    Exchange,
    TransactionSide,
)


class Portfolio(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid4())
    )
    name: str
    currency: Currency = Currency.INR
    initial_cash: Decimal
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class PortfolioTransaction(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid4())
    )
    portfolio_id: str
    idempotency_key: str

    symbol: str
    exchange: Exchange
    side: TransactionSide

    quantity: Decimal
    executed_price: Decimal
    gross_amount: Decimal
    fees: Decimal
    net_cash_effect: Decimal

    executed_at: datetime = Field(default_factory=utc_now)


class CreatePortfolioRequest(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
    )
    initial_cash: Decimal = Field(gt=0)


class CreateTradeRequest(BaseModel):
    idempotency_key: str = Field(
        min_length=8,
        max_length=100,
    )
    symbol: str = Field(
        min_length=1,
        max_length=20,
    )
    side: TransactionSide
    quantity: Decimal = Field(gt=0)


class PortfolioLedgerState(BaseModel):
    cash_balance: Decimal
    quantities: dict[str, Decimal]


class TradeExecutionResponse(BaseModel):
    transaction: PortfolioTransaction
    remaining_cash: Decimal
    position_quantity: Decimal

class PositionValuation(BaseModel):
    symbol: str
    exchange: Exchange
    currency: Currency

    quantity: Decimal
    average_cost: Decimal
    cost_basis: Decimal

    current_price: Decimal
    market_value: Decimal

    unrealized_pnl: Decimal
    unrealized_return_percent: Decimal


class PortfolioSummary(BaseModel):
    portfolio_id: str
    portfolio_name: str
    currency: Currency

    initial_cash: Decimal
    cash_balance: Decimal

    positions_cost_basis: Decimal
    positions_market_value: Decimal
    total_portfolio_value: Decimal

    realized_pnl: Decimal
    unrealized_pnl: Decimal
    total_pnl: Decimal
    total_return_percent: Decimal
    total_fees: Decimal

    positions: list[PositionValuation]

class PortfolioRiskMetrics(BaseModel):
    portfolio_id: str
    observation_count: int
    trading_days_per_year: int = 252

    annualized_return_percent: Decimal
    annualized_volatility_percent: Decimal
    sharpe_ratio: Decimal | None
    maximum_drawdown_percent: Decimal

    value_at_risk_95_percent: Decimal
    value_at_risk_95_amount: Decimal

    largest_position_symbol: str | None
    largest_position_weight_percent: Decimal
    open_position_count: int

    risk_free_rate_percent: Decimal
    data_status: str