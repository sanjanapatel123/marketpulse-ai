import asyncio
import json
from collections.abc import AsyncIterator
from dataclasses import dataclass
from time import monotonic
from uuid import uuid4

import httpx

from app.services.stock_analyzer import build_analysis


API_URL = "http://127.0.0.1:8000"
DISCONNECT_AFTER = 10
MINIMUM_TEXT_EVENTS = 30
WAIT_TIMEOUT_SECONDS = 10

TERMINAL_EVENTS = {
    "run_completed",
    "run_failed",
    "run_interrupted",
}


@dataclass(frozen=True)
class ReceivedEvent:
    sequence: int
    event_type: str
    payload: dict


async def parse_sse(
    response: httpx.Response,
) -> AsyncIterator[ReceivedEvent]:
    event_id: str | None = None
    event_type = "message"
    data_lines: list[str] = []

    async for line in response.aiter_lines():
        if line == "":
            if data_lines:
                data = json.loads("\n".join(data_lines))

                yield ReceivedEvent(
                    sequence=int(
                        data.get("sequence", event_id)
                    ),
                    event_type=event_type,
                    payload=data.get("payload", {}),
                )

            event_id = None
            event_type = "message"
            data_lines = []
            continue

        if line.startswith(":"):
            continue

        field, separator, value = line.partition(":")

        if not separator:
            continue

        value = value.lstrip()

        if field == "id":
            event_id = value
        elif field == "event":
            event_type = value
        elif field == "data":
            data_lines.append(value)


async def receive_first_events(
    client: httpx.AsyncClient,
    run_id: str,
    count: int,
) -> list[ReceivedEvent]:
    received: list[ReceivedEvent] = []

    stream_url = (
        f"{API_URL}/api/runs/{run_id}/events"
    )

    async with client.stream(
        "GET",
        stream_url,
        params={"cursor": 0},
    ) as response:
        response.raise_for_status()

        async for event in parse_sse(response):
            received.append(event)

            if len(received) >= count:
                # Leaving this context closes the SSE connection.
                break

    return received


async def wait_for_events_during_disconnect(
    client: httpx.AsyncClient,
    run_id: str,
    disconnect_cursor: int,
) -> dict:
    deadline = monotonic() + WAIT_TIMEOUT_SECONDS
    required_sequence = disconnect_cursor + 5

    while monotonic() < deadline:
        response = await client.get(
            f"{API_URL}/api/runs/{run_id}"
        )
        response.raise_for_status()

        body = response.json()
        run = body["run"]

        if (
            run["last_sequence"] >= required_sequence
            or run["status"] != "running"
        ):
            return run

        await asyncio.sleep(0.05)

    raise TimeoutError(
        "Timed out waiting for events during disconnection"
    )


async def receive_after_cursor(
    client: httpx.AsyncClient,
    run_id: str,
    cursor: int,
) -> list[ReceivedEvent]:
    received: list[ReceivedEvent] = []

    async with client.stream(
        "GET",
        f"{API_URL}/api/runs/{run_id}/events",
        params={"cursor": cursor},
    ) as response:
        response.raise_for_status()

        async for event in parse_sse(response):
            received.append(event)

            if event.event_type in TERMINAL_EVENTS:
                break

    return received


def verify_benchmark(
    *,
    first_connection: list[ReceivedEvent],
    second_connection: list[ReceivedEvent],
    expected_text: str,
    final_run: dict,
) -> dict:
    combined_events = (
        first_connection + second_connection
    )

    sequences = [
        event.sequence
        for event in combined_events
    ]

    unique_sequences = set(sequences)

    duplicate_count = (
        len(sequences) - len(unique_sequences)
    )

    final_sequence = max(sequences, default=0)

    expected_sequences = set(
        range(1, final_sequence + 1)
    )

    missing_sequences = sorted(
        expected_sequences - unique_sequences
    )

    text_events = [
        event
        for event in combined_events
        if event.event_type == "text_delta"
    ]

    reconstructed_text = "".join(
        event.payload.get("text", "")
        for event in text_events
    )

    ordered = sequences == sorted(sequences)

    terminal_events = [
        event.event_type
        for event in combined_events
        if event.event_type in TERMINAL_EVENTS
    ]

    checks = {
        "minimum_30_text_events": (
            len(text_events) >= MINIMUM_TEXT_EVENTS
        ),
        "zero_duplicates": duplicate_count == 0,
        "zero_missing": len(missing_sequences) == 0,
        "ordered": ordered,
        "exact_response_match": (
            reconstructed_text == expected_text
        ),
        "completed": (
            final_run["status"] == "completed"
        ),
        "one_terminal_event": (
            terminal_events == ["run_completed"]
        ),
    }

    return {
        "passed": all(checks.values()),
        "checks": checks,
        "observed_event_count": len(combined_events),
        "observed_text_event_count": len(text_events),
        "disconnect_cursor": (
            first_connection[-1].sequence
        ),
        "first_replayed_sequence": (
            second_connection[0].sequence
            if second_connection
            else None
        ),
        "duplicate_count": duplicate_count,
        "missing_sequences": missing_sequences,
        "final_run_state": final_run["status"],
        "final_sequence": final_sequence,
    }


async def main() -> None:
    stock_symbol = "RELIANCE"
    question = (
        "Explain the company fundamentals, valuation "
        "and major risks."
    )

    timeout = httpx.Timeout(
        connect=5,
        read=None,
        write=10,
        pool=5,
    )

    async with httpx.AsyncClient(
        timeout=timeout
    ) as client:
        health_response = await client.get(
            f"{API_URL}/api/health"
        )
        health_response.raise_for_status()

        create_response = await client.post(
            f"{API_URL}/api/analyses",
            json={
                "message_id": (
                    f"benchmark-{uuid4()}"
                ),
                "stock_symbol": stock_symbol,
                "question": question,
            },
        )
        create_response.raise_for_status()

        analysis = create_response.json()
        run_id = analysis["run_id"]

        print(f"Run ID: {run_id}")
        print(
            f"Connecting until event "
            f"{DISCONNECT_AFTER}..."
        )

        first_connection = await receive_first_events(
            client=client,
            run_id=run_id,
            count=DISCONNECT_AFTER,
        )

        disconnect_cursor = (
            first_connection[-1].sequence
        )

        print(
            f"Connection interrupted at cursor "
            f"{disconnect_cursor}"
        )

        disconnected_run = (
            await wait_for_events_during_disconnect(
                client=client,
                run_id=run_id,
                disconnect_cursor=disconnect_cursor,
            )
        )

        generated_while_disconnected = (
            disconnected_run["last_sequence"]
            - disconnect_cursor
        )

        print(
            "Events generated while disconnected: "
            f"{generated_while_disconnected}"
        )

        print(
            f"Reconnecting from cursor "
            f"{disconnect_cursor}..."
        )

        second_connection = await receive_after_cursor(
            client=client,
            run_id=run_id,
            cursor=disconnect_cursor,
        )

        final_response = await client.get(
            f"{API_URL}/api/runs/{run_id}"
        )
        final_response.raise_for_status()

        final_run = final_response.json()["run"]

        result = verify_benchmark(
            first_connection=first_connection,
            second_connection=second_connection,
            expected_text=build_analysis(
                stock_symbol,
                question,
            ),
            final_run=final_run,
        )

        print()
        print("Verification benchmark")
        print("----------------------")
        print(
            f"Observed events: "
            f"{result['observed_event_count']}"
        )
        print(
            f"Text events: "
            f"{result['observed_text_event_count']}"
        )
        print(
            f"Disconnect cursor: "
            f"{result['disconnect_cursor']}"
        )
        print(
            f"First replayed sequence: "
            f"{result['first_replayed_sequence']}"
        )
        print(
            f"Duplicate events: "
            f"{result['duplicate_count']}"
        )
        print(
            f"Missing events: "
            f"{len(result['missing_sequences'])}"
        )
        print(
            f"Final run state: "
            f"{result['final_run_state']}"
        )

        for check_name, passed in result[
            "checks"
        ].items():
            marker = "PASS" if passed else "FAIL"
            print(f"[{marker}] {check_name}")

        print()
        print(
            "BENCHMARK PASSED"
            if result["passed"]
            else "BENCHMARK FAILED"
        )

        if not result["passed"]:
            raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())