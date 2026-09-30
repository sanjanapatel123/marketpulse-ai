import asyncio
from uuid import uuid4

from app.core.database import (
    close_database,
    create_indexes,
    ping_database,
)
from app.models.notification import (
    NotificationEvent,
    NotificationEventType,
    NotificationPayload,
)
from app.repositories.notification_repository import (
    create_notification_event,
    get_latest_notification_cursor,
    list_notifications_after_cursor,
)


TOTAL_EVENTS = 30
DISCONNECT_AFTER = 10


def create_payload(
    benchmark_id: str,
    event_number: int,
) -> NotificationPayload:
    alert_id = (
        f"benchmark-{benchmark_id}-{event_number:02d}"
    )

    return NotificationPayload(
        alert_id=alert_id,
        watchlist_id="benchmark-watchlist",
        symbol="TCS",
        exchange="NSE",
        currency="INR",
        condition="PRICE_ABOVE",
        threshold=str(
            4200 + event_number
        ),
        triggered_price=str(
            4201 + event_number
        ),
        title=(
            f"Benchmark notification "
            f"{event_number:02d}"
        ),
        message=(
            f"Deterministic benchmark event "
            f"{event_number:02d} of {TOTAL_EVENTS}."
        ),
    )


async def generate_event(
    benchmark_id: str,
    event_number: int,
) -> NotificationEvent:
    source_id = (
        f"benchmark-{benchmark_id}-{event_number:02d}"
    )

    return await create_notification_event(
        event_type=(
            NotificationEventType
            .PRICE_ALERT_TRIGGERED
        ),
        source_type="notification_benchmark",
        source_id=source_id,
        payload=create_payload(
            benchmark_id=benchmark_id,
            event_number=event_number,
        ),
    )


def is_benchmark_event(
    event: NotificationEvent,
    benchmark_id: str,
) -> bool:
    return (
        event.source_type
        == "notification_benchmark"
        and event.source_id.startswith(
            f"benchmark-{benchmark_id}-"
        )
    )


async def main() -> None:
    benchmark_id = uuid4().hex[:12]

    await ping_database()
    await create_indexes()

    try:
        starting_cursor = (
            await get_latest_notification_cursor()
        )

        print(
            f"Benchmark ID: {benchmark_id}"
        )
        print(
            f"Starting cursor: {starting_cursor}"
        )
        print(
            f"Generating first "
            f"{DISCONNECT_AFTER} events..."
        )

        for event_number in range(
            1,
            DISCONNECT_AFTER + 1,
        ):
            await generate_event(
                benchmark_id=benchmark_id,
                event_number=event_number,
            )

        first_delivery = (
            await list_notifications_after_cursor(
                cursor=starting_cursor,
                limit=500,
            )
        )

        first_benchmark_events = [
            event
            for event in first_delivery
            if is_benchmark_event(
                event,
                benchmark_id,
            )
        ]

        if not first_delivery:
            raise RuntimeError(
                "Initial delivery returned no events"
            )

        # A real client checkpoints every received event,
        # including any unrelated event in the same stream.
        disconnect_cursor = max(
            event.sequence
            for event in first_delivery
        )

        print(
            f"Connection interrupted at cursor "
            f"{disconnect_cursor}"
        )

        print(
            f"Generating "
            f"{TOTAL_EVENTS - DISCONNECT_AFTER} "
            "events while disconnected..."
        )

        for event_number in range(
            DISCONNECT_AFTER + 1,
            TOTAL_EVENTS + 1,
        ):
            await generate_event(
                benchmark_id=benchmark_id,
                event_number=event_number,
            )

        print(
            f"Reconnecting from cursor "
            f"{disconnect_cursor}..."
        )

        replay_delivery = (
            await list_notifications_after_cursor(
                cursor=disconnect_cursor,
                limit=500,
            )
        )

        replayed_benchmark_events = [
            event
            for event in replay_delivery
            if is_benchmark_event(
                event,
                benchmark_id,
            )
        ]

        observed_events = (
            first_benchmark_events
            + replayed_benchmark_events
        )

        observed_source_ids = [
            event.source_id
            for event in observed_events
        ]

        expected_source_ids = [
            (
                f"benchmark-{benchmark_id}-"
                f"{event_number:02d}"
            )
            for event_number in range(
                1,
                TOTAL_EVENTS + 1,
            )
        ]

        duplicate_count = (
            len(observed_source_ids)
            - len(set(observed_source_ids))
        )

        missing_source_ids = (
            set(expected_source_ids)
            - set(observed_source_ids)
        )

        sequences = [
            event.sequence
            for event in observed_events
        ]

        ordered = sequences == sorted(sequences)

        checks = {
            "minimum_30_events": (
                len(observed_events)
                >= TOTAL_EVENTS
            ),
            "zero_duplicates": (
                duplicate_count == 0
            ),
            "zero_missing": (
                len(missing_source_ids) == 0
            ),
            "ordered": ordered,
            "exact_event_identity": (
                observed_source_ids
                == expected_source_ids
            ),
            "reconnected_after_cursor": (
                not replayed_benchmark_events
                or (
                    replayed_benchmark_events[0]
                    .sequence
                    > disconnect_cursor
                )
            ),
        }

        print()
        print("Notification reconnect benchmark")
        print("--------------------------------")
        print(
            f"Observed events: "
            f"{len(observed_events)}"
        )
        print(
            f"Events before disconnect: "
            f"{len(first_benchmark_events)}"
        )
        print(
            f"Events replayed: "
            f"{len(replayed_benchmark_events)}"
        )
        print(
            f"Disconnect cursor: "
            f"{disconnect_cursor}"
        )
        print(
            f"Duplicate events: "
            f"{duplicate_count}"
        )
        print(
            f"Missing events: "
            f"{len(missing_source_ids)}"
        )
        print(
            f"Ordered: {ordered}"
        )

        for check_name, passed in checks.items():
            status = "PASS" if passed else "FAIL"

            print(
                f"[{status}] {check_name}"
            )

        if not all(checks.values()):
            raise RuntimeError(
                "NOTIFICATION BENCHMARK FAILED"
            )

        print()
        print(
            "NOTIFICATION BENCHMARK PASSED"
        )

    finally:
        await close_database()


if __name__ == "__main__":
    asyncio.run(main())