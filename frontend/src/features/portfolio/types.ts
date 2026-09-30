export type TransactionSide = "BUY" | "SELL";

export interface Portfolio {
  id: string;
  name: string;
  currency: string;
  initial_cash: string;
  created_at: string;
  updated_at: string;
}

export interface PortfolioTransaction {
  id: string;
  portfolio_id: string;
  idempotency_key: string;
  symbol: string;
  exchange: string;
  side: TransactionSide;
  quantity: string;
  executed_price: string;
  gross_amount: string;
  fees: string;
  net_cash_effect: string;
  executed_at: string;
}

export interface PositionValuation {
  symbol: string;
  exchange: string;
  currency: string;
  quantity: string;
  average_cost: string;
  cost_basis: string;
  current_price: string;
  market_value: string;
  unrealized_pnl: string;
  unrealized_return_percent: string;
}

export interface PortfolioSummary {
  portfolio_id: string;
  portfolio_name: string;
  currency: string;
  initial_cash: string;
  cash_balance: string;
  positions_cost_basis: string;
  positions_market_value: string;
  total_portfolio_value: string;
  realized_pnl: string;
  unrealized_pnl: string;
  total_pnl: string;
  total_return_percent: string;
  total_fees: string;
  positions: PositionValuation[];
}

export interface PortfolioListResponse {
  data: Portfolio[];
  count: number;
}

export interface PortfolioDetailResponse {
  portfolio: Portfolio;
  transactions: PortfolioTransaction[];
}

export interface TradeInput {
  idempotency_key: string;
  symbol: string;
  side: TransactionSide;
  quantity: string;
}

export interface PortfolioRiskMetrics {
  portfolio_id: string;
  observation_count: number;
  trading_days_per_year: number;

  annualized_return_percent: string;
  annualized_volatility_percent: string;
  sharpe_ratio: string | null;
  maximum_drawdown_percent: string;

  value_at_risk_95_percent: string;
  value_at_risk_95_amount: string;

  largest_position_symbol: string | null;
  largest_position_weight_percent: string;
  open_position_count: number;

  risk_free_rate_percent: string;
  data_status: string;
}