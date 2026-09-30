
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.workers.alert_monitor import AlertMonitor


@pytest.mark.asyncio
async def test_alert_monitor_evaluates_once():
    evaluation_result = SimpleNamespace(
        evaluated_count=2,
        triggered_count=1,
        triggered_alerts=[
            SimpleNamespace(
                id="alert-test-001",
                symbol="TCS",
                condition="PRICE_BELOW",
                threshold="4300.00",
                triggered_price="4215.60",
            )
        ],
    )

    evaluator = AsyncMock(
        return_value=evaluation_result
    )

    monitor = AlertMonitor(
        interval_seconds=15,
        evaluator=evaluator,
    )

    result = await monitor.evaluate_once()

    evaluator.assert_awaited_once_with()
    assert result is evaluation_result
    assert result.evaluated_count == 2
    assert result.triggered_count == 1


@pytest.mark.asyncio
async def test_alert_monitor_handles_evaluation_failure():
    evaluator = AsyncMock(
        side_effect=RuntimeError("Market provider unavailable")
    )

    monitor = AlertMonitor(
        interval_seconds=15,
        evaluator=evaluator,
    )

    result = await monitor.evaluate_once()

    evaluator.assert_awaited_once_with()
    assert result is None


def test_alert_monitor_rejects_invalid_interval():
    with pytest.raises(
        ValueError,
        match="interval_seconds must be greater than zero",
    ):
        AlertMonitor(interval_seconds=0)