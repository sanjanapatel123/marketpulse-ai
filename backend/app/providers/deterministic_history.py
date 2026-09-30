from datetime import (
    date,
    datetime,
    time,
    timedelta,
    timezone,
)
from decimal import Decimal, ROUND_HALF_UP
from uuid import NAMESPACE_URL, uuid5

from app.models.enums import (
    Currency,
    Exchange,
    MarketDataStatus,
)
from app.models.market import PriceCandle


TWOPLACES = Decimal("0.01")

BASE_PRICES = {
    "RELIANCE": Decimal("2700.00"),
    "TCS": Decimal("3900.00"),
    "INFY": Decimal("1650.00"),
}

BASE_VOLUMES = {
    "RELIANCE": 7_500_000,
    "TCS": 1_900_000,
    "INFY": 5_200_000,
}

SYMBOL_SEEDS = {
    "RELIANCE": 11,
    "TCS": 23,
    "INFY": 37,
}


def money(value: Decimal) -> Decimal:
    return value.quantize(
        TWOPLACES,
        rounding=ROUND_HALF_UP,
    )


def trading_days(
    *,
    end_date: date,
    count: int,
) -> list[date]:
    days: list[date] = []
    current_date = end_date

    while len(days) < count:
        if current_date.weekday() < 5:
            days.append(current_date)

        current_date -= timedelta(days=1)

    days.reverse()
    return days


def generate_price_history(
    *,
    symbol: str,
    end_date: date,
    days: int = 90,
) -> list[PriceCandle]:
    normalized_symbol = symbol.strip().upper()

    if normalized_symbol not in BASE_PRICES:
        raise ValueError(
            f"Price history unavailable for "
            f"{normalized_symbol}"
        )

    dates = trading_days(
        end_date=end_date,
        count=days,
    )

    seed = SYMBOL_SEEDS[normalized_symbol]
    previous_close = BASE_PRICES[normalized_symbol]
    base_volume = BASE_VOLUMES[normalized_symbol]

    candles: list[PriceCandle] = []

    for index, trading_date in enumerate(dates):
        open_bps = (
            ((index * 17 + seed) % 61) - 30
        )

        close_bps = (
            ((index * 37 + seed) % 161) - 80
        )

        range_bps = Decimal(
            35 + ((index * 13 + seed) % 31)
        )

        open_price = money(
            previous_close
            * (
                Decimal("1")
                + Decimal(open_bps)
                / Decimal("10000")
            )
        )

        close_price = money(
            open_price
            * (
                Decimal("1")
                + Decimal(close_bps)
                / Decimal("10000")
            )
        )

        high_price = money(
            max(open_price, close_price)
            * (
                Decimal("1")
                + range_bps / Decimal("10000")
            )
        )

        low_price = money(
            min(open_price, close_price)
            * (
                Decimal("1")
                - range_bps / Decimal("10000")
            )
        )

        return_percent = money(
            (
                (close_price - previous_close)
                / previous_close
            )
            * Decimal("100")
        )

        timestamp = datetime.combine(
            trading_date,
            time(hour=10),
            tzinfo=timezone.utc,
        )

        deterministic_id = str(
            uuid5(
                NAMESPACE_URL,
                (
                    f"marketpulse:{normalized_symbol}:"
                    f"{timestamp.isoformat()}:1d"
                ),
            )
        )

        volume = (
            base_volume
            + ((index * 97_531 + seed) % 1_500_000)
        )

        candles.append(
            PriceCandle(
                id=deterministic_id,
                symbol=normalized_symbol,
                exchange=Exchange.NSE,
                currency=Currency.INR,
                timestamp=timestamp,
                open=open_price,
                high=high_price,
                low=low_price,
                close=close_price,
                previous_close=previous_close,
                return_percent=return_percent,
                volume=volume,
                data_status=(
                    MarketDataStatus.SIMULATED
                ),
                provider=(
                    "deterministic-history-provider"
                ),
            )
        )

        previous_close = close_price

    return candles