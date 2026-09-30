import asyncio
import json
from collections.abc import AsyncIterator

from fastapi import Request

from app.models.enums import RunStatus
from app.repositories.run_repository import (
    find_events_after,
    find_run,
)

TERMINAL_STATUSES = {
    RunStatus.COMPLETED.value,
    RunStatus.FAILED.value,
    RunStatus.INTERRUPTED.value,
}


def serialize_event(event: dict) -> dict[str, str]:
    sequence = event["sequence"]

    data = {
        "id": event["id"],
        "run_id": event["run_id"],
        "sequence": sequence,
        "type": event["type"],
        "payload": event["payload"],
        "created_at": event["created_at"].isoformat(),
    }

    return {
        "id": str(sequence),
        "event": event["type"],
        "data": json.dumps(data),
    }


async def stream_run_events(
    *,
    request: Request,
    run_id: str,
    initial_cursor: int,
    poll_interval: float = 0.1,
) -> AsyncIterator[dict[str, str]]:
    cursor = initial_cursor

    while True:
        if await request.is_disconnected():
            return

        events = await find_events_after(
            run_id=run_id,
            cursor=cursor,
        )

        for event in events:
            sequence = event["sequence"]

            # Defensive protection against duplicate/out-of-order display.
            if sequence <= cursor:
                continue

            # Every next durable event must be contiguous.
            if sequence != cursor + 1:
                yield {
                    "event": "stream_error",
                    "data": json.dumps(
                        {
                            "code": "EVENT_GAP",
                            "message": (
                                f"Expected sequence {cursor + 1}, "
                                f"received {sequence}"
                            ),
                            "recoverable": True,
                        }
                    ),
                }
                return

            yield serialize_event(event)
            cursor = sequence

        run = await find_run(run_id)

        if run is None:
            yield {
                "event": "stream_error",
                "data": json.dumps(
                    {
                        "code": "RUN_NOT_FOUND",
                        "message": "Run is no longer available",
                        "recoverable": False,
                    }
                ),
            }
            return

        if (
            run["status"] in TERMINAL_STATUSES
            and cursor >= run["last_sequence"]
        ):
            return

        await asyncio.sleep(poll_interval)