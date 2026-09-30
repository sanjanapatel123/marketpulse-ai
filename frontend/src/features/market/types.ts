export interface Stock {
  id: string;
  symbol: string;
  company_name: string;
  exchange: string;
  currency: string;
  sector: string;
  industry: string;
  isin: string | null;
  is_active: boolean;
}

export interface MarketQuote {
  id: string;
  symbol: string;
  exchange: string;
  currency: string;
  price: string;
  previous_close: string;
  change: string;
  change_percent: string;
  open: string;
  day_high: string;
  day_low: string;
  volume: number;
  as_of: string;
  data_status: string;
  provider: string;
}

export interface PriceCandle {
  id: string;
  symbol: string;
  exchange: string;
  currency: string;
  interval: "1d";
  timestamp: string;
  open: string;
  high: string;
  low: string;
  close: string;
  previous_close: string | null;
  return_percent: string | null;
  volume: number;
  data_status: string;
  provider: string;
}

export interface StockListResponse {
  data: Stock[];
  count: number;
}

export interface PriceHistoryResponse {
  symbol: string;
  exchange: string;
  currency: string;
  interval: "1d";
  provider: string;
  data_status: string;
  count: number;
  candles: PriceCandle[];
}

export type HistoryRange = 30 | 60 | 90;

export interface FinancialStatement {
  id: string;
  symbol: string;
  exchange: string;
  fiscal_year: string;
  currency: string;
  unit: "INR_CRORE";

  revenue: string;
  ebitda: string;
  ebit: string;
  net_income: string;

  total_assets: string;
  shareholder_equity: string;
  total_debt: string;
  current_assets: string;
  current_liabilities: string;
  shares_outstanding: string;

  data_status: string;
  provider: string;
  reported_at: string;
}

export interface FundamentalRatios {
  symbol: string;
  fiscal_year: string;
  currency: string;

  earnings_per_share: string;
  book_value_per_share: string;
  price_to_earnings: string;
  price_to_book: string;
  return_on_equity_percent: string;
  return_on_capital_employed_percent: string;
  net_profit_margin_percent: string;
  revenue_growth_percent: string | null;
  debt_to_equity: string;
  current_ratio: string;
}

export interface FundamentalsResponse {
  symbol: string;
  exchange: string;
  data_status: string;
  provider: string;
  latest_statement: FinancialStatement;
  previous_statement: FinancialStatement | null;
  ratios: FundamentalRatios;
}