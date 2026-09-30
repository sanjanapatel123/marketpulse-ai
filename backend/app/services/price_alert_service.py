import asyncio
from datetime import UTC, datetime, timezone
from decimal import Decimal

from app.models.enums import Exchange
from app.models.watchlist import (
    AlertEvaluationResult,
    PriceAlert,
)
from app.repositories.watchlist_repository import (
    list_active_alerts,
    mark_alert_triggered,
)
from app.services.market_service import market_provider
from app.services.price_alert_engine import (
    should_trigger_price_alert,
)

from app.services.notification_service import (
    reconcile_price_alert_notifications,
)


async def evaluate_price_alerts(
) -> AlertEvaluationResult:
    active_alerts = await list_active_alerts()
    evaluated_at = datetime.now(timezone.utc)

    if not active_alerts:
        return AlertEvaluationResult(
            evaluated_count=0,
            triggered_count=0,
            triggered_alerts=[],
            evaluated_at=evaluated_at,
        )

    unique_symbols = sorted(
        {
            alert.symbol
            for alert in active_alerts
        }
    )

    async def load_price(
        symbol: str,
    ) -> tuple[str, Decimal]:
        quote = await market_provider.get_quote(
            symbol=symbol,
            exchange=Exchange.NSE,
        )

        return symbol, quote.price

    quote_results = await asyncio.gather(
        *[
            load_price(symbol)
            for symbol in unique_symbols
        ]
    )

    prices_by_symbol = dict(quote_results)

    triggered_alerts: list[PriceAlert] = []

    for alert in active_alerts:
        current_price = prices_by_symbol[
            alert.symbol
        ]

        triggered = should_trigger_price_alert(
            condition=alert.condition,
            threshold=alert.threshold,
            current_price=current_price,
        )

        if not triggered:
            continue

        updated_alert = await mark_alert_triggered(
            alert_id=alert.id,
            triggered_price=current_price,
            triggered_at=evaluated_at,
        )

        # None means another evaluator already triggered it.
        if updated_alert is not None:
            triggered_alerts.append(
                updated_alert
            )

    await reconcile_price_alert_notifications()

    evaluated_at = datetime.now(UTC)

    return AlertEvaluationResult(
        evaluated_count=len(active_alerts),
        triggered_count=len(triggered_alerts),
        triggered_alerts=triggered_alerts,
        evaluated_at=evaluated_at,
    )