import pytest

from app.services.stock_analyzer import (
    build_analysis,
    generate_stock_analysis,
    split_into_chunks,
)


@pytest.mark.asyncio
async def test_generator_produces_at_least_30_ordered_chunks():
    chunks = [
        chunk
        async for chunk in generate_stock_analysis(
            symbol="RELIANCE",
            question="Explain the fundamentals and risks.",
        )
    ]

    assert len(chunks) >= 30
    assert [chunk.position for chunk in chunks] == list(
        range(1, len(chunks) + 1)
    )


@pytest.mark.asyncio
async def test_generator_is_deterministic():
    parameters = {
        "symbol": "TCS",
        "question": "Explain the company.",
    }

    first_result = [
        chunk.text
        async for chunk in generate_stock_analysis(**parameters)
    ]

    second_result = [
        chunk.text
        async for chunk in generate_stock_analysis(**parameters)
    ]

    assert first_result == second_result


@pytest.mark.asyncio
async def test_generator_failure_after_partial_output():
    received_chunks = []

    with pytest.raises(
        RuntimeError,
        match="failed after 5 chunks",
    ):
        async for chunk in generate_stock_analysis(
            symbol="INFY",
            question="Explain the risks.",
            fail_after=5,
        ):
            received_chunks.append(chunk)

    assert len(received_chunks) == 5
    assert [chunk.position for chunk in received_chunks] == [
        1,
        2,
        3,
        4,
        5,
    ]


def test_chunks_reconstruct_original_analysis():
    analysis = build_analysis(
        "RELIANCE",
        "Explain its fundamentals.",
    )

    chunks = split_into_chunks(analysis)

    assert "".join(chunks) == analysis


def test_invalid_chunk_size():
    with pytest.raises(
        ValueError,
        match="must be greater than zero",
    ):
        split_into_chunks("example analysis", words_per_chunk=0)