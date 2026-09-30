from datetime import date

from app.providers.deterministic_history import (
    generate_price_history,
)


def test_generates_requested_trading_days():
    candles = generate_price_history(
        symbol="RELIANCE",
        end_date=date(2026, 9, 28),
        days=90,
    )

    assert len(candles) == 90

    assert all(
        candle.timestamp.weekday() < 5
        for candle in candles
    )


def test_ohlc_values_are_financially_valid():
    candles = generate_price_history(
        symbol="TCS",
        end_date=date(2026, 9, 28),
        days=30,
    )

    for candle in candles:
        assert candle.high >= candle.open
        assert candle.high >= candle.close
        assert candle.low <= candle.open
        assert candle.low <= candle.close
        assert candle.low > 0
        assert candle.volume > 0


def test_history_is_deterministic():
    parameters = {
        "symbol": "INFY",
        "end_date": date(2026, 9, 28),
        "days": 30,
    }

    first = generate_price_history(**parameters)
    second = generate_price_history(**parameters)

    assert first == second


def test_previous_close_chain_is_correct():
    candles = generate_price_history(
        symbol="RELIANCE",
        end_date=date(2026, 9, 28),
        days=30,
    )

    for index in range(1, len(candles)):
        assert (
            candles[index].previous_close
            == candles[index - 1].close
        )