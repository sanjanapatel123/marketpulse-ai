export type ConnectionState =
  | "idle"
  | "connecting"
  | "connected"
  | "reconnecting"
  | "disconnected"
  | "completed"
  | "failed"
  | "interrupted";

export interface CreateAnalysisInput {
  conversation_id?: string | null;
  message_id: string;
  stock_symbol: string;
  question: string;
}

export interface CreateAnalysisResponse {
  conversation_id: string;
  message_id: string;
  run_id: string;
  status: string;
  stream_url: string;
}