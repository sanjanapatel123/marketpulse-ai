from app.models.enums import EventType
from app.repositories.run_repository import (
    claim_run_for_generation,
    find_message_by_id,
    mark_run_completed,
    mark_run_failed,
    persist_event,
)
from app.services.stock_analyzer import generate_stock_analysis


async def generate_run(
    run_id: str,
    *,
    delay_seconds: float = 0.15,
    fail_after: int | None = None,
) -> None:
    run = await claim_run_for_generation(run_id)

    # Another request/process already claimed this run.
    if run is None:
        return

    message = await find_message_by_id(run["user_message_id"])

    if message is None:
        await mark_run_failed(
            run_id=run_id,
            error_message="User message not found",
            last_sequence=run["last_sequence"],
        )
        return

    last_sequence = 0

    try:
        async for chunk in generate_stock_analysis(
            symbol=message["stock_symbol"],
            question=message["content"],
            delay_seconds=delay_seconds,
            fail_after=fail_after,
        ):
            await persist_event(
                run_id=run_id,
                sequence=chunk.position,
                event_type=EventType.TEXT_DELTA,
                payload={
                    "text": chunk.text,
                },
            )

            last_sequence = chunk.position

    except Exception as error:
        failure_sequence = last_sequence + 1
        error_message = str(error)

        transitioned = await mark_run_failed(
            run_id=run_id,
            error_message=error_message,
            last_sequence=failure_sequence,
        )

        if transitioned:
            await persist_event(
                run_id=run_id,
                sequence=failure_sequence,
                event_type=EventType.RUN_FAILED,
                payload={
                    "message": error_message,
                },
            )

        return

    completed_sequence = last_sequence + 1

    transitioned = await mark_run_completed(
        run_id=run_id,
        last_sequence=completed_sequence,
    )

    if transitioned:
        await persist_event(
            run_id=run_id,
            sequence=completed_sequence,
            event_type=EventType.RUN_COMPLETED,
            payload={},
        )