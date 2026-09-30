import type {
  FundamentalsResponse,
  MarketQuote,
  PriceHistoryResponse,
  StockListResponse,
} from "../types";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000";

async function apiRequest<T>(
  path: string,
): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);

    const message =
      body?.detail?.message ??
      body?.detail ??
      "Market data request failed";

    throw new Error(message);
  }

  return response.json();
}

export function getStocks() {
  return apiRequest<StockListResponse>(
    "/api/market/stocks",
  );
}

export function getQuote(symbol: string) {
  return apiRequest<MarketQuote>(
    `/api/market/quotes/${symbol}`,
  );
}

export function getPriceHistory(
  symbol: string,
  days: number,
) {
  return apiRequest<PriceHistoryResponse>(
    `/api/market/stocks/${symbol}/history?days=${days}`,
  );
}

export function getFundamentals(symbol: string) {
  return apiRequest<FundamentalsResponse>(
    `/api/market/stocks/${symbol}/fundamentals`,
  );
}