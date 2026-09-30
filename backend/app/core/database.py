from pymongo import ASCENDING, AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from app.core.config import get_settings

settings = get_settings()

client: AsyncMongoClient = AsyncMongoClient(
    settings.mongodb_url,
    tz_aware=True,
)
database: AsyncDatabase = client[settings.mongodb_database]


async def ping_database() -> None:
    await client.admin.command("ping")


async def create_indexes() -> None:
    await database.conversations.create_index(
        [("id", ASCENDING)],
        unique=True,
    )

    await database.conversations.create_index(
        [("updated_at", ASCENDING)]
    )

    await database.messages.create_index(
        [("id", ASCENDING)],
        unique=True,
    )

    await database.runs.create_index(
        [("id", ASCENDING)],
        unique=True,
    )

    await database.runs.create_index(
        [("user_message_id", ASCENDING)],
        unique=True,
    )

    await database.run_events.create_index(
        [("run_id", ASCENDING), ("sequence", ASCENDING)],
        unique=True,
    )

    await database.stocks.create_index(
    [
        ("symbol", ASCENDING),
        ("exchange", ASCENDING),
    ],
    unique=True,
    )

    await database.stocks.create_index(
    [
        ("sector", ASCENDING),
        ("is_active", ASCENDING),
    ]
    )

    await database.market_quotes.create_index(
    [
        ("symbol", ASCENDING),
        ("exchange", ASCENDING),
        ("as_of", -1),
    ]
    )

    await database.market_quotes.create_index(
    [
        ("received_at", ASCENDING),
    ],
    expireAfterSeconds=60 * 60 * 24 * 30,
    )

    await database.price_candles.create_index(
    [
        ("metadata.symbol", ASCENDING),
        ("metadata.interval", ASCENDING),
        ("timestamp", -1),
    ]
    )

    await database.financial_statements.create_index(
    [
        ("symbol", ASCENDING),
        ("fiscal_year", ASCENDING),
    ],
    unique=True,
    )
    await database.portfolios.create_index(
    [("id", ASCENDING)],
    unique=True,
)

    await database.portfolio_transactions.create_index(
    [
        ("portfolio_id", ASCENDING),
        ("idempotency_key", ASCENDING),
    ],
    unique=True,
)

    await database.portfolio_transactions.create_index(
    [
        ("portfolio_id", ASCENDING),
        ("symbol", ASCENDING),
        ("executed_at", ASCENDING),
    ]
)
    await database.watchlists.create_index(
    [("id", ASCENDING)],
    unique=True,
)

    await database.watchlist_items.create_index(
    [
        ("watchlist_id", ASCENDING),
        ("symbol", ASCENDING),
        ("exchange", ASCENDING),
    ],
    unique=True,
)

    await database.price_alerts.create_index(
    [("id", ASCENDING)],
    unique=True,
)

    await database.price_alerts.create_index(
    [
        ("status", ASCENDING),
        ("symbol", ASCENDING),
    ]
)
    await database.notification_events.create_index(
    [("id", 1)],
    unique=True,
    name="uq_notification_event_id",
)
    
    await database.notification_events.create_index(
    [("sequence", 1)],
    unique=True,
    name="uq_notification_sequence",
)

    await database.notification_events.create_index(
    [
        ("source_type", 1),
        ("source_id", 1),
    ],
    unique=True,
    name="uq_notification_source",
)

    await database.notification_events.create_index(
    [("created_at", -1)],
    name="idx_notification_created_at",
)
    await database.event_counters.create_index(
    [("name", 1)],
    unique=True,
    name="uq_event_counter_name",
)


async def create_market_collections() -> None:
    collection_names = (
        await database.list_collection_names()
    )

    if "price_candles" not in collection_names:
        await database.create_collection(
            "price_candles",
            timeseries={
                "timeField": "timestamp",
                "metaField": "metadata",
                "granularity": "hours",
            },
        )

async def close_database() -> None:
    await client.close()