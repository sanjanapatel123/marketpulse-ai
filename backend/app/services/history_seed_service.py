from datetime import datetime, timezone

from app.providers.deterministic_history import (
    generate_price_history,
)
from app.repositories.market_repository import (
    save_missing_candles,
)


HISTORY_SYMBOLS = [
    "RELIANCE",
    "TCS",
    "INFY",
]


async def seed_price_history() -> int:
    total_inserted = 0
    today = datetime.now(timezone.utc).date()

    for symbol in HISTORY_SYMBOLS:
        candles = generate_price_history(
            symbol=symbol,
            end_date=today,
            days=90,
        )

        inserted_count = await save_missing_candles(
            candles
        )

        total_inserted += inserted_count

    return total_inserted