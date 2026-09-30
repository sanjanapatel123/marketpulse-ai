from app.models.enums import EventType, RunStatus
from app.repositories.run_repository import (
    find_event_at_sequence,
    find_runs_by_status,
    mark_run_interrupted,
    persist_event,
)

RESTART_REASON = (
    "Generation was interrupted because the service restarted"
)

TERMINAL_EVENT_TYPES = {
    RunStatus.COMPLETED: EventType.RUN_COMPLETED,
    RunStatus.FAILED: EventType.RUN_FAILED,
    RunStatus.INTERRUPTED: EventType.RUN_INTERRUPTED,
}


async def recover_runs_after_restart() -> int:
    running_runs = await find_runs_by_status(
        RunStatus.RUNNING
    )

    interrupted_count = 0

    for run in running_runs:
        terminal_sequence = run["last_sequence"] + 1

        transitioned = await mark_run_interrupted(
            run_id=run["id"],
            reason=RESTART_REASON,
            last_sequence=terminal_sequence,
        )

        if not transitioned:
            continue

        await persist_event(
            run_id=run["id"],
            sequence=terminal_sequence,
            event_type=EventType.RUN_INTERRUPTED,
            payload={
                "message": RESTART_REASON,
                "recoverable": True,
            },
        )

        interrupted_count += 1

    return interrupted_count


async def reconcile_terminal_events() -> int:
    repaired_count = 0

    for run_status, event_type in TERMINAL_EVENT_TYPES.items():
        runs = await find_runs_by_status(run_status)

        for run in runs:
            if run["last_sequence"] <= 0:
                continue

            existing_event = await find_event_at_sequence(
                run_id=run["id"],
                sequence=run["last_sequence"],
            )

            if existing_event is not None:
                continue

            payload: dict = {}

            if run_status in {
                RunStatus.FAILED,
                RunStatus.INTERRUPTED,
            }:
                payload = {
                    "message": (
                        run.get("error_message")
                        or "Run ended unexpectedly"
                    )
                }

            await persist_event(
                run_id=run["id"],
                sequence=run["last_sequence"],
                event_type=event_type,
                payload=payload,
            )

            repaired_count += 1

    return repaired_count