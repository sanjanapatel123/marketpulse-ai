export type Exchange = "NSE";

export type Currency = "INR";

export type MarketDataStatus = "simulated" | "live";

export type PriceAlertCondition = "PRICE_ABOVE" | "PRICE_BELOW";

export type PriceAlertStatus = "ACTIVE" | "TRIGGERED" | "DISABLED";

export interface Watchlist {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface WatchlistItem {
  id: string;
  watchlist_id: string;
  symbol: string;
  exchange: Exchange;
  added_at: string;
}

export interface WatchlistItemQuote {
  item: WatchlistItem;
  company_name: string;
  sector: string;
  price: string;
  change: string;
  change_percent: string;
  currency: Currency;
  data_status: MarketDataStatus;
}

export interface PriceAlert {
  id: string;
  watchlist_id: string;
  symbol: string;
  exchange: Exchange;
  currency: Currency;
  condition: PriceAlertCondition;
  threshold: string;
  status: PriceAlertStatus;
  triggered_price: string | null;
  triggered_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface WatchlistDetail {
  watchlist: Watchlist;
  items: WatchlistItemQuote[];
  alerts: PriceAlert[];
}

export interface WatchlistCollectionResponse {
  data: Watchlist[];
  count: number;
}

export interface CreateWatchlistInput {
  name: string;
}

export interface AddWatchlistItemInput {
  symbol: string;
  exchange: Exchange;
}

export interface CreatePriceAlertInput {
  symbol: string;
  exchange: Exchange;
  condition: PriceAlertCondition;
  threshold: string;
}

export interface AlertEvaluationResult {
  evaluated_count: number;
  triggered_count: number;
  triggered_alerts: PriceAlert[];
  evaluated_at: string;
}
