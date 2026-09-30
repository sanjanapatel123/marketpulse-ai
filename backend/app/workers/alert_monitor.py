import asyncio
import logging
from collections.abc import Awaitable, Callable
from contextlib import suppress
from typing import Any

from app.services.price_alert_service import evaluate_price_alerts


logger = logging.getLogger("uvicorn.error")

AlertEvaluator = Callable[[], Awaitable[Any]]


class AlertMonitor:
    def __init__(
        self,
        interval_seconds: int = 15,
        evaluator: AlertEvaluator = evaluate_price_alerts,
    ) -> None:
        if interval_seconds <= 0:
            raise ValueError(
                "interval_seconds must be greater than zero"
            )

        self.interval_seconds = interval_seconds
        self.evaluator = evaluator

        self._task: asyncio.Task[None] | None = None
        self._stop_event = asyncio.Event()

    async def evaluate_once(self) -> Any:
        """
        Runs one alert-evaluation cycle.

        Kept separate from the periodic loop so it can be
        tested without arbitrary sleeps.
        """
        try:
            result = await self.evaluator()

            logger.info(
                "Alert evaluation completed: "
                "evaluated=%s triggered=%s",
                result.evaluated_count,
                result.triggered_count,
            )

            for alert in result.triggered_alerts:
                logger.info(
                    "Price alert triggered: "
                    "alert_id=%s symbol=%s condition=%s "
                    "threshold=%s triggered_price=%s",
                    alert.id,
                    alert.symbol,
                    alert.condition,
                    alert.threshold,
                    alert.triggered_price,
                )

            return result

        except asyncio.CancelledError:
            raise

        except Exception:
            # A temporary provider/database failure should not
            # permanently terminate the background worker.
            logger.exception(
                "Background alert evaluation failed"
            )
            return None

    async def _run(self) -> None:
        logger.info(
            "Price alert monitor started: interval=%s seconds",
            self.interval_seconds,
        )

        while not self._stop_event.is_set():
            await self.evaluate_once()

            try:
                await asyncio.wait_for(
                    self._stop_event.wait(),
                    timeout=self.interval_seconds,
                )
            except asyncio.TimeoutError:
                # Expected: run another evaluation cycle.
                continue

        logger.info("Price alert monitor loop stopped")

    def start(self) -> None:
        """
        Starts the monitor once.

        Calling start repeatedly will not create duplicate tasks.
        """
        if self._task is not None and not self._task.done():
            return

        self._stop_event.clear()

        self._task = asyncio.create_task(
            self._run(),
            name="price-alert-monitor",
        )

    async def stop(self) -> None:
        """
        Stops the monitor gracefully during FastAPI shutdown.
        """
        self._stop_event.set()

        if self._task is None:
            return

        self._task.cancel()

        with suppress(asyncio.CancelledError):
            await self._task

        self._task = None