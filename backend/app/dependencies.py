from fastapi import Request

from app.services.watchlist_service import WatchlistService


def get_watchlist_service(request: Request) -> WatchlistService:
    return request.app.state.watchlist_service