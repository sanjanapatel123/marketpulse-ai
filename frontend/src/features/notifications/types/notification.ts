export type NotificationConnectionState =
  | "connected"
  | "reconnecting"
  | "disconnected";

export type NotificationEventType = "price_alert_triggered";

export interface NotificationPayload {
  alert_id: string;
  watchlist_id: string;
  symbol: string;
  exchange: string;
  currency: string;
  condition: string;
  threshold: string;
  triggered_price: string;
  title: string;
  message: string;
}

export interface NotificationEvent {
  id: string;
  sequence: number;
  type: NotificationEventType;
  source_id: string;
  source_type: string;
  payload: NotificationPayload;
  created_at: string;
}

export interface NotificationHistoryResponse {
  events: NotificationEvent[];
  count: number;
  latest_cursor: number;
}
