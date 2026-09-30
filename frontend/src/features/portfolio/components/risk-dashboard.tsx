import {
  Activity,
  AlertTriangle,
  ChartSpline,
  Gauge,
  ShieldAlert,
  Target,
  TrendingDown,
  TrendingUp,
} from "lucide-react";

import { formatCurrency } from "../../../features/market/market-utils";

import type { PortfolioRiskMetrics } from "../types";
import { RiskMetricCard } from "./risk-metric-card";

interface RiskDashboardProps {
  risk: PortfolioRiskMetrics;
}

export function RiskDashboard({ risk }: RiskDashboardProps) {
  const annualizedReturn = Number(risk.annualized_return_percent);

  const sharpe = Number(risk.sharpe_ratio ?? 0);

  const concentration = Number(risk.largest_position_weight_percent);

  const isConcentrated = concentration > 50;

  return (
    <section className="rounded-[28px] border border-white/[0.08] bg-[#10141f]/85 p-6">
      <div className="flex flex-col gap-4 border-b border-white/[0.06] pb-6 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-start gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-400/10 text-purple-300">
            <ShieldAlert className="h-5 w-5" />
          </div>

          <div>
            <h2 className="font-semibold text-white">Portfolio risk</h2>

            <p className="mt-1 text-xs text-slate-500">
              Based on {risk.observation_count} simulated daily-return
              observations
            </p>
          </div>
        </div>

        <div className="rounded-xl border border-amber-400/20 bg-amber-400/[0.06] px-3 py-2 text-xs text-amber-300">
          {risk.data_status} data
        </div>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <RiskMetricCard
          label="Annualized return"
          value={`${annualizedReturn.toFixed(2)}%`}
          description="Estimated yearly return from observed daily returns."
          icon={annualizedReturn >= 0 ? TrendingUp : TrendingDown}
          tone={annualizedReturn >= 0 ? "positive" : "negative"}
        />

        <RiskMetricCard
          label="Annualized volatility"
          value={`${Number(risk.annualized_volatility_percent).toFixed(2)}%`}
          description="Annualized variability of portfolio daily returns."
          icon={Activity}
        />

        <RiskMetricCard
          label="Sharpe ratio"
          value={risk.sharpe_ratio === null ? "N/A" : sharpe.toFixed(2)}
          description={`Risk-adjusted return using a ${risk.risk_free_rate_percent}% risk-free assumption.`}
          icon={Gauge}
          tone={
            risk.sharpe_ratio === null
              ? "neutral"
              : sharpe >= 0
                ? "positive"
                : "negative"
          }
        />

        <RiskMetricCard
          label="Maximum drawdown"
          value={`${Number(risk.maximum_drawdown_percent).toFixed(2)}%`}
          description="Largest historical peak-to-trough decline."
          icon={TrendingDown}
          tone="negative"
        />

        <RiskMetricCard
          label="One-day VaR 95%"
          value={`${Number(risk.value_at_risk_95_percent).toFixed(2)}%`}
          description="Historical one-day loss boundary at 95% confidence."
          icon={Target}
          tone="warning"
        />

        <RiskMetricCard
          label="VaR amount"
          value={formatCurrency(risk.value_at_risk_95_amount)}
          description="Estimated monetary loss boundary on invested value."
          icon={AlertTriangle}
          tone="warning"
        />

        <RiskMetricCard
          label="Open positions"
          value={String(risk.open_position_count)}
          description="Number of securities with a positive quantity."
          icon={ChartSpline}
        />

        <RiskMetricCard
          label="Largest position"
          value={`${concentration.toFixed(2)}%`}
          description={
            risk.largest_position_symbol
              ? `${risk.largest_position_symbol} share of invested market value.`
              : "No open equity position."
          }
          icon={ShieldAlert}
          tone={isConcentrated ? "warning" : "neutral"}
        />
      </div>

      {isConcentrated && risk.largest_position_symbol && (
        <div className="mt-6 rounded-2xl border border-amber-400/20 bg-amber-400/[0.06] p-5">
          <div className="flex gap-3">
            <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-amber-300" />

            <div>
              <p className="text-sm font-medium text-amber-200">
                High position concentration
              </p>

              <p className="mt-1 text-xs leading-5 text-amber-200/60">
                {risk.largest_position_symbol} represents{" "}
                {concentration.toFixed(2)}% of invested market value. This
                metric describes concentration and is not personalized
                investment advice.
              </p>

              <div className="mt-4 h-2 overflow-hidden rounded-full bg-black/30">
                <div
                  className="h-full rounded-full bg-amber-400"
                  style={{
                    width: `${Math.min(concentration, 100)}%`,
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      <p className="mt-5 text-xs leading-5 text-slate-600">
        Historical risk metrics do not predict maximum future losses. Market
        gaps and unprecedented events may exceed the observed range.
      </p>
    </section>
  );
}
