import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass


@dataclass(frozen=True)
class GeneratedChunk:
    position: int
    text: str


STOCK_FIXTURES: dict[str, dict[str, str]] = {
    "RELIANCE": {
        "company_name": "Reliance Industries Limited",
        "sector": "Diversified",
        "business": (
            "energy, petrochemicals, retail, telecommunications "
            "and digital services"
        ),
        "strength": (
            "diversified revenue streams and strong market presence"
        ),
        "risk": (
            "capital intensity, regulatory changes and commodity cycles"
        ),
    },
    "TCS": {
        "company_name": "Tata Consultancy Services",
        "sector": "Information Technology",
        "business": (
            "IT services, consulting, cloud and digital transformation"
        ),
        "strength": (
            "recurring enterprise relationships and global delivery"
        ),
        "risk": (
            "currency movements, global slowdown and pricing pressure"
        ),
    },
    "INFY": {
        "company_name": "Infosys Limited",
        "sector": "Information Technology",
        "business": (
            "technology consulting, outsourcing and digital services"
        ),
        "strength": (
            "global client relationships and scalable delivery capability"
        ),
        "risk": (
            "client spending reductions and employee cost pressure"
        ),
    },
}

DEFAULT_FIXTURE = {
    "company_name": "the selected company",
    "sector": "Unknown",
    "business": "business operations reported by the company",
    "strength": "its established operating capabilities",
    "risk": "market, financial and execution uncertainty",
}


def build_analysis(symbol: str, question: str) -> str:
    normalized_symbol = symbol.strip().upper()
    fixture = STOCK_FIXTURES.get(normalized_symbol, DEFAULT_FIXTURE)

    return (
        f"Educational analysis for {normalized_symbol}. "
        f"{fixture['company_name']} operates in the "
        f"{fixture['sector']} sector. "
        f"Its primary activities include {fixture['business']}. "
        f"A potential business strength is {fixture['strength']}. "
        f"Important risks include {fixture['risk']}. "
        "Revenue growth should be evaluated across multiple reporting "
        "periods instead of relying on one quarter. "
        "Profit growth should also be compared with cash-flow generation. "
        "Debt levels matter because high borrowing can increase financial "
        "risk when interest rates rise. "
        "Return on equity can indicate how efficiently shareholder capital "
        "is being used. "
        "Valuation ratios such as price-to-earnings should be compared with "
        "the company history and relevant competitors. "
        "A high valuation may imply strong expectations that the business "
        "must continue to satisfy. "
        "The bull case depends on profitable growth, execution quality and "
        "sustained competitive advantages. "
        "The bear case includes slower demand, margin pressure, regulation "
        "and unsuccessful capital allocation. "
        f"The user asked: {question.strip()} "
        "This deterministic response is generated for protocol testing and "
        "is not personalized financial advice."
    )


def split_into_chunks(
    text: str,
    words_per_chunk: int = 4,
) -> list[str]:
    if words_per_chunk <= 0:
        raise ValueError("words_per_chunk must be greater than zero")

    words = text.split()
    chunks: list[str] = []

    for index in range(0, len(words), words_per_chunk):
        chunk_words = words[index:index + words_per_chunk]
        chunk = " ".join(chunk_words)

        if index + words_per_chunk < len(words):
            chunk += " "

        chunks.append(chunk)

    return chunks


async def generate_stock_analysis(
    *,
    symbol: str,
    question: str,
    delay_seconds: float = 0,
    fail_after: int | None = None,
) -> AsyncIterator[GeneratedChunk]:
    analysis = build_analysis(symbol, question)
    chunks = split_into_chunks(analysis)

    for position, text in enumerate(chunks, start=1):
        if fail_after is not None and position > fail_after:
            raise RuntimeError(
                f"Fake stock analyzer failed after {fail_after} chunks"
            )

        if delay_seconds > 0:
            await asyncio.sleep(delay_seconds)

        yield GeneratedChunk(
            position=position,
            text=text,
        )