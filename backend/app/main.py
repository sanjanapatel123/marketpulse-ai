from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analyses import router as analyses_router
from app.api.market import router as market_router
from app.api.portfolios import router as portfolios_router
from app.api.runs import router as runs_router
from app.api.watchlists import router as watchlists_router
from app.api.notifications import (
    router as notifications_router,
)
from app.core.config import get_settings
from app.core.database import (
    close_database,
    create_indexes,
    create_market_collections,
    ping_database,
)

from app.services.fundamental_seed_service import seed_fundamentals
from app.services.history_seed_service import seed_price_history
from app.services.restart_recovery_service import (
    reconcile_terminal_events,
    recover_runs_after_restart,
)
from app.services.stock_seed_service import seed_stocks

from app.workers.alert_monitor import AlertMonitor


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    alert_monitor: AlertMonitor | None = None

    try:
        # -------------------------------------------------
        # Database startup
        # -------------------------------------------------

        await ping_database()
        await create_market_collections()
        await create_indexes()

        # -------------------------------------------------
        # Deterministic market-data seeding
        # -------------------------------------------------

        seeded_stocks = await seed_stocks()
        seeded_candles = await seed_price_history()
        seeded_fundamentals = await seed_fundamentals()

        # -------------------------------------------------
        # Durable run recovery
        # -------------------------------------------------

        interrupted_count = await recover_runs_after_restart()
        repaired_count = await reconcile_terminal_events()

        print("MongoDB connected and indexes created")

        print(
            f"Stock master ready: "
            f"{seeded_stocks} stocks"
        )

        print(
            f"Historical prices ready: "
            f"{seeded_candles} new candles"
        )

        print(
            f"Fundamentals ready: "
            f"{seeded_fundamentals} new statements"
        )

        print(
            f"Restart recovery: "
            f"{interrupted_count} runs interrupted, "
            f"{repaired_count} terminal events repaired"
        )

        # -------------------------------------------------
        # Automatic price-alert monitoring
        # -------------------------------------------------

        if settings.enable_alert_monitor:
            alert_monitor = AlertMonitor(
                interval_seconds=(
                    settings.alert_evaluation_interval_seconds
                ),
            )

            alert_monitor.start()

            app.state.alert_monitor = alert_monitor

            print(
                "Price alert monitor started: "
                f"interval="
                f"{settings.alert_evaluation_interval_seconds}s"
            )
        else:
            print("Price alert monitor disabled")

        yield

    finally:
        # Stop worker before closing MongoDB.
        if alert_monitor is not None:
            await alert_monitor.stop()
            print("Price alert monitor stopped")

        await close_database()
        print("MongoDB connection closed")


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------
# Middleware
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# API routers
# ---------------------------------------------------------

app.include_router(market_router)
app.include_router(analyses_router)
app.include_router(runs_router)
app.include_router(portfolios_router)
app.include_router(watchlists_router)
app.include_router(notifications_router)

# ---------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------

@app.get(
    "/api/health",
    tags=["Health"],
)
async def health_check():
    return {
        "success": True,
        "message": "MarketPulse AI service is running",
        "database": "connected",
        "alert_monitor": (
            "enabled"
            if settings.enable_alert_monitor
            else "disabled"
        ),
    }