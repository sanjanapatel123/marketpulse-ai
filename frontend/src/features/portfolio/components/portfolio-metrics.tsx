import {
  Banknote,
  ChartNoAxesCombined,
  CircleDollarSign,
  Landmark,
} from "lucide-react";

import { MetricCard } from "../../../components/ui/metric-card";
import { formatCurrency } from "../../../features/market/market-utils";

import type { PortfolioSummary } from "../types";

interface PortfolioMetricsProps {
  summary: PortfolioSummary;
}

export function PortfolioMetrics({ summary }: PortfolioMetricsProps) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <MetricCard
        label="Total value"
        value={formatCurrency(summary.total_portfolio_value)}
        icon={Landmark}
      />

      <MetricCard
        label="Available cash"
        value={formatCurrency(summary.cash_balance)}
        icon={Banknote}
      />

      <MetricCard
        label="Invested value"
        value={formatCurrency(summary.positions_market_value)}
        icon={ChartNoAxesCombined}
      />

      <MetricCard
        label="Total P&L"
        value={formatCurrency(summary.total_pnl)}
        icon={CircleDollarSign}
      />
    </div>
  );
}
