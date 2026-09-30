from app.providers.deterministic_fundamentals import (
    generate_financial_statements,
)
from app.repositories.fundamental_repository import (
    save_financial_statements,
)


SYMBOLS = ["RELIANCE", "TCS", "INFY"]


async def seed_fundamentals() -> int:
    total_saved = 0

    for symbol in SYMBOLS:
        statements = (
            generate_financial_statements(symbol)
        )

        total_saved += (
            await save_financial_statements(
                statements
            )
        )

    return total_saved