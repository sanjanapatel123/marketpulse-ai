from datetime import datetime, timezone
from typing import Any

import pytest

import app.services.restart_recovery_service as recovery_service
import app.services.run_generation_service as generation_service
import app.services.run_stream_service as stream_service
from app.models.enums import EventType, RunStatus


class FakeRequest:
    async def is_disconnected(self) -> bool:
        return False


def make_event(
    sequence: int,
    event_type: str = "text_delta",
    text: str | None = None,
) -> dict[str, Any]:
    payload = {}

    if text is not None:
        payload["text"] = text

    return {
        "id": f"event-{sequence}",
        "run_id": "run-test",
        "sequence": sequence,
        "type": event_type,
        "payload": payload,
        "created_at": datetime.now(timezone.utc),
    }


@pytest.mark.asyncio
async def test_ordered_live_event_delivery(monkeypatch):
    event_batches = {
        0: [
            make_event(1, text="first "),
        ],
        1: [
            make_event(2, text="second "),
            make_event(3, "run_completed"),
        ],
    }

    run_checks = 0

    async def fake_find_events_after(
        run_id: str,
        cursor: int,
    ) -> list[dict]:
        return event_batches.get(cursor, [])

    async def fake_find_run(run_id: str) -> dict:
        nonlocal run_checks
        run_checks += 1

        if run_checks == 1:
            return {
                "id": run_id,
                "status": "running",
                "last_sequence": 1,
            }

        return {
            "id": run_id,
            "status": "completed",
            "last_sequence": 3,
        }

    monkeypatch.setattr(
        stream_service,
        "find_events_after",
        fake_find_events_after,
    )
    monkeypatch.setattr(
        stream_service,
        "find_run",
        fake_find_run,
    )

    received = [
        event
        async for event in stream_service.stream_run_events(
            request=FakeRequest(),
            run_id="run-test",
            initial_cursor=0,
            poll_interval=0,
        )
    ]

    assert [event["id"] for event in received] == [
        "1",
        "2",
        "3",
    ]

    assert [event["event"] for event in received] == [
        "text_delta",
        "text_delta",
        "run_completed",
    ]


@pytest.mark.asyncio
async def test_replay_after_cursor(monkeypatch):
    stored_events = [
        make_event(1, text="one "),
        make_event(2, text="two "),
        make_event(3, text="three "),
        make_event(4, "run_completed"),
    ]

    async def fake_find_events_after(
        run_id: str,
        cursor: int,
    ) -> list[dict]:
        return [
            event
            for event in stored_events
            if event["sequence"] > cursor
        ]

    async def fake_find_run(run_id: str) -> dict:
        return {
            "id": run_id,
            "status": "completed",
            "last_sequence": 4,
        }

    monkeypatch.setattr(
        stream_service,
        "find_events_after",
        fake_find_events_after,
    )
    monkeypatch.setattr(
        stream_service,
        "find_run",
        fake_find_run,
    )

    received = [
        event
        async for event in stream_service.stream_run_events(
            request=FakeRequest(),
            run_id="run-test",
            initial_cursor=2,
            poll_interval=0,
        )
    ]

    assert [event["id"] for event in received] == [
        "3",
        "4",
    ]


@pytest.mark.asyncio
async def test_replay_live_overlap_is_deduplicated(
    monkeypatch,
):
    query_count = 0

    async def fake_find_events_after(
        run_id: str,
        cursor: int,
    ) -> list[dict]:
        nonlocal query_count
        query_count += 1

        if query_count == 1:
            return [
                make_event(2, text="second "),
                make_event(3, text="third "),
            ]

        # Event 3 intentionally overlaps with the previous query.
        return [
            make_event(3, text="third "),
            make_event(4, "run_completed"),
        ]

    async def fake_find_run(run_id: str) -> dict:
        if query_count == 1:
            return {
                "id": run_id,
                "status": "running",
                "last_sequence": 3,
            }

        return {
            "id": run_id,
            "status": "completed",
            "last_sequence": 4,
        }

    monkeypatch.setattr(
        stream_service,
        "find_events_after",
        fake_find_events_after,
    )
    monkeypatch.setattr(
        stream_service,
        "find_run",
        fake_find_run,
    )

    received = [
        event
        async for event in stream_service.stream_run_events(
            request=FakeRequest(),
            run_id="run-test",
            initial_cursor=1,
            poll_interval=0,
        )
    ]

    assert [event["id"] for event in received] == [
        "2",
        "3",
        "4",
    ]

    assert len(received) == 3


@pytest.mark.asyncio
async def test_generator_failure_preserves_partial_events(
    monkeypatch,
):
    persisted_events: list[dict] = []
    failed_transition: dict = {}
    completed_called = False

    async def fake_claim_run(run_id: str) -> dict:
        return {
            "id": run_id,
            "user_message_id": "message-test",
            "last_sequence": 0,
            "status": "running",
        }

    async def fake_find_message(message_id: str) -> dict:
        return {
            "id": message_id,
            "stock_symbol": "INFY",
            "content": "Explain the risks.",
        }

    async def fake_persist_event(**kwargs):
        persisted_events.append(kwargs)
        return kwargs

    async def fake_mark_failed(**kwargs) -> bool:
        failed_transition.update(kwargs)
        return True

    async def fake_mark_completed(**kwargs) -> bool:
        nonlocal completed_called
        completed_called = True
        return True

    monkeypatch.setattr(
        generation_service,
        "claim_run_for_generation",
        fake_claim_run,
    )
    monkeypatch.setattr(
        generation_service,
        "find_message_by_id",
        fake_find_message,
    )
    monkeypatch.setattr(
        generation_service,
        "persist_event",
        fake_persist_event,
    )
    monkeypatch.setattr(
        generation_service,
        "mark_run_failed",
        fake_mark_failed,
    )
    monkeypatch.setattr(
        generation_service,
        "mark_run_completed",
        fake_mark_completed,
    )

    await generation_service.generate_run(
        "run-test",
        delay_seconds=0,
        fail_after=3,
    )

    assert [
        event["sequence"]
        for event in persisted_events
    ] == [1, 2, 3, 4]

    assert [
        event["event_type"]
        for event in persisted_events
    ] == [
        EventType.TEXT_DELTA,
        EventType.TEXT_DELTA,
        EventType.TEXT_DELTA,
        EventType.RUN_FAILED,
    ]

    assert failed_transition["last_sequence"] == 4
    assert "failed after 3 chunks" in (
        failed_transition["error_message"]
    )

    assert completed_called is False


@pytest.mark.asyncio
async def test_running_run_becomes_interrupted_after_restart(
    monkeypatch,
):
    persisted_events: list[dict] = []
    interrupted_transition: dict = {}

    async def fake_find_runs_by_status(
        run_status: RunStatus,
    ) -> list[dict]:
        assert run_status == RunStatus.RUNNING

        return [
            {
                "id": "run-restart",
                "status": "running",
                "last_sequence": 5,
            }
        ]

    async def fake_mark_interrupted(**kwargs) -> bool:
        interrupted_transition.update(kwargs)
        return True

    async def fake_persist_event(**kwargs):
        persisted_events.append(kwargs)
        return kwargs

    monkeypatch.setattr(
        recovery_service,
        "find_runs_by_status",
        fake_find_runs_by_status,
    )
    monkeypatch.setattr(
        recovery_service,
        "mark_run_interrupted",
        fake_mark_interrupted,
    )
    monkeypatch.setattr(
        recovery_service,
        "persist_event",
        fake_persist_event,
    )

    interrupted_count = (
        await recovery_service.recover_runs_after_restart()
    )

    assert interrupted_count == 1

    assert interrupted_transition["run_id"] == (
        "run-restart"
    )
    assert interrupted_transition["last_sequence"] == 6

    assert len(persisted_events) == 1
    assert persisted_events[0]["sequence"] == 6
    assert persisted_events[0]["event_type"] == (
        EventType.RUN_INTERRUPTED
    )