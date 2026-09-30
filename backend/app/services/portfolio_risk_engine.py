from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from math import sqrt
from statistics import mean, stdev

from app.models.portfolio import (
    PortfolioRiskMetrics,
)


TRADING_DAYS = 252
TWO_PLACES = Decimal("0.01")
HUNDRED = Decimal("100")


def rounded(value: float | Decimal) -> Decimal:
    return Decimal(str(value)).quantize(
        TWO_PLACES,
        rounding=ROUND_HALF_UP,
    )


def calculate_portfolio_risk(
    *,
    portfolio_id: str,
    position_values: dict[str, Decimal],
    returns_by_symbol: dict[
        str,
        dict[date, Decimal],
    ],
    risk_free_rate: Decimal = Decimal("0.06"),
) -> PortfolioRiskMetrics:
    total_position_value = sum(
        position_values.values(),
        Decimal("0"),
    )

    if total_position_value <= 0:
        return PortfolioRiskMetrics(
            portfolio_id=portfolio_id,
            observation_count=0,
            annualized_return_percent=Decimal("0"),
            annualized_volatility_percent=(
                Decimal("0")
            ),
            sharpe_ratio=None,
            maximum_drawdown_percent=Decimal("0"),
            value_at_risk_95_percent=Decimal("0"),
            value_at_risk_95_amount=Decimal("0"),
            largest_position_symbol=None,
            largest_position_weight_percent=(
                Decimal("0")
            ),
            open_position_count=0,
            risk_free_rate_percent=rounded(
                risk_free_rate * HUNDRED
            ),
            data_status="simulated",
        )

    weights = {
        symbol: value / total_position_value
        for symbol, value in position_values.items()
        if value > 0
    }

    available_date_sets = [
        set(returns_by_symbol[symbol].keys())
        for symbol in weights
        if symbol in returns_by_symbol
    ]

    if len(available_date_sets) != len(weights):
        raise ValueError(
            "Historical returns unavailable for "
            "one or more positions"
        )

    common_dates = sorted(
        set.intersection(*available_date_sets)
    )

    if len(common_dates) < 2:
        raise ValueError(
            "Insufficient historical observations"
        )

    portfolio_returns: list[float] = []

    for observation_date in common_dates:
        daily_return = sum(
            (
                weights[symbol]
                * returns_by_symbol[symbol][
                    observation_date
                ]
            )
            for symbol in weights
        )

        portfolio_returns.append(
            float(daily_return)
        )

    average_daily_return = mean(
        portfolio_returns
    )

    daily_volatility = (
        stdev(portfolio_returns)
        if len(portfolio_returns) > 1
        else 0.0
    )

    annualized_return = (
        average_daily_return * TRADING_DAYS
    )

    annualized_volatility = (
        daily_volatility * sqrt(TRADING_DAYS)
    )

    sharpe_ratio: Decimal | None = None

    if annualized_volatility > 0:
        sharpe_ratio = rounded(
            (
                annualized_return
                - float(risk_free_rate)
            )
            / annualized_volatility
        )

    cumulative_value = 1.0
    peak_value = 1.0
    maximum_drawdown = 0.0

    for daily_return in portfolio_returns:
        cumulative_value *= 1 + daily_return
        peak_value = max(
            peak_value,
            cumulative_value,
        )

        drawdown = (
            cumulative_value / peak_value
        ) - 1

        maximum_drawdown = min(
            maximum_drawdown,
            drawdown,
        )

    sorted_returns = sorted(portfolio_returns)

    var_index = max(
        0,
        int(len(sorted_returns) * 0.05),
    )

    fifth_percentile_return = (
        sorted_returns[var_index]
    )

    value_at_risk_percent = max(
        0.0,
        -fifth_percentile_return,
    )

    value_at_risk_amount = (
        total_position_value
        * Decimal(str(value_at_risk_percent))
    )

    largest_position_symbol = max(
        weights,
        key=weights.get,  # type: ignore[arg-type]
    )

    largest_position_weight = (
        weights[largest_position_symbol]
    )

    return PortfolioRiskMetrics(
        portfolio_id=portfolio_id,
        observation_count=len(
            portfolio_returns
        ),
        annualized_return_percent=rounded(
            annualized_return * 100
        ),
        annualized_volatility_percent=rounded(
            annualized_volatility * 100
        ),
        sharpe_ratio=sharpe_ratio,
        maximum_drawdown_percent=rounded(
            maximum_drawdown * 100
        ),
        value_at_risk_95_percent=rounded(
            value_at_risk_percent * 100
        ),
        value_at_risk_95_amount=rounded(
            value_at_risk_amount
        ),
        largest_position_symbol=(
            largest_position_symbol
        ),
        largest_position_weight_percent=rounded(
            largest_position_weight * HUNDRED
        ),
        open_position_count=len(weights),
        risk_free_rate_percent=rounded(
            risk_free_rate * HUNDRED
        ),
        data_status="simulated",
    )