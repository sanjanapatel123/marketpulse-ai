from app.models.enums import Exchange
from app.models.market import Stock
from app.repositories.market_repository import upsert_stock


STOCKS = [
    Stock(
        symbol="RELIANCE",
        company_name="Reliance Industries Limited",
        exchange=Exchange.NSE,
        sector="Diversified",
        industry="Oil, Retail and Telecommunications",
        isin="INE002A01018",
    ),
    Stock(
        symbol="TCS",
        company_name="Tata Consultancy Services",
        exchange=Exchange.NSE,
        sector="Information Technology",
        industry="IT Services and Consulting",
        isin="INE467B01029",
    ),
    Stock(
        symbol="INFY",
        company_name="Infosys Limited",
        exchange=Exchange.NSE,
        sector="Information Technology",
        industry="IT Services and Consulting",
        isin="INE009A01021",
    ),
]


async def seed_stocks() -> int:
    for stock in STOCKS:
        await upsert_stock(stock)

    return len(STOCKS)