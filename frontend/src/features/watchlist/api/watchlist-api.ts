import type {
  AddWatchlistItemInput,
  AlertEvaluationResult,
  CreatePriceAlertInput,
  CreateWatchlistInput,
  PriceAlert,
  Watchlist,
  WatchlistCollectionResponse,
  WatchlistDetail,
  WatchlistItem,
} from "../types/watchlist";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function parseApiResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let message = "Request failed";

    try {
      const errorBody = await response.json();

      message = errorBody.detail ?? errorBody.message ?? message;
    } catch {
      message = response.statusText || message;
    }

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export async function getWatchlists(): Promise<WatchlistCollectionResponse> {
  const response = await fetch(`${API_URL}/api/watchlists`, {
    cache: "no-store",
  });

  return parseApiResponse<WatchlistCollectionResponse>(response);
}

export async function getWatchlistDetail(
  watchlistId: string,
): Promise<WatchlistDetail> {
  const response = await fetch(
    `${API_URL}/api/watchlists/${encodeURIComponent(watchlistId)}`,
    {
      cache: "no-store",
    },
  );

  return parseApiResponse<WatchlistDetail>(response);
}

export async function createWatchlist(
  payload: CreateWatchlistInput,
): Promise<Watchlist> {
  const response = await fetch(`${API_URL}/api/watchlists`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  return parseApiResponse<Watchlist>(response);
}

export async function addWatchlistItem(
  watchlistId: string,
  payload: AddWatchlistItemInput,
): Promise<WatchlistItem> {
  const response = await fetch(
    `${API_URL}/api/watchlists/${encodeURIComponent(watchlistId)}/items`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    },
  );

  return parseApiResponse<WatchlistItem>(response);
}

export async function removeWatchlistItem(
  watchlistId: string,
  symbol: string,
): Promise<void> {
  const response = await fetch(
    `${API_URL}/api/watchlists/${encodeURIComponent(
      watchlistId,
    )}/items/${encodeURIComponent(symbol)}`,
    {
      method: "DELETE",
    },
  );

  if (!response.ok) {
    let message = "Unable to remove stock";

    try {
      const errorBody = await response.json();
      message = errorBody.detail ?? message;
    } catch {
      // Keep fallback error message.
    }

    throw new Error(message);
  }
}

export async function createPriceAlert(
  watchlistId: string,
  payload: CreatePriceAlertInput,
): Promise<PriceAlert> {
  const response = await fetch(
    `${API_URL}/api/watchlists/${encodeURIComponent(watchlistId)}/alerts`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    },
  );

  return parseApiResponse<PriceAlert>(response);
}

export async function evaluateAlerts(): Promise<AlertEvaluationResult> {
  const response = await fetch(`${API_URL}/api/watchlists/alerts/evaluate`, {
    method: "POST",
  });

  return parseApiResponse<AlertEvaluationResult>(response);
}
