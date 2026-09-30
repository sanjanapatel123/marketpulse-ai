import {
  Activity,
  BadgeIndianRupee,
  Banknote,
  BookOpen,
  ChartNoAxesCombined,
  CircleGauge,
  Percent,
  Scale,
  TrendingUp,
  WalletCards,
} from "lucide-react";

import { formatCurrency, formatPercent, formatRatio } from "../market-utils";

import type { FundamentalsResponse } from "../types";
import { FinancialComparisonChart } from "./financial-comparison-chart";
import { RatioCard } from "./ratio-card";

interface FundamentalsPanelProps {
  fundamentals: FundamentalsResponse;
}

export function FundamentalsPanel({ fundamentals }: FundamentalsPanelProps) {
  const { ratios, latest_statement, previous_statement } = fundamentals;

  return (
    <section className="rounded-[28px] border border-white/[0.08] bg-[#10141f]/85 p-6 shadow-2xl shadow-black/20 backdrop-blur-xl">
      <div className="flex flex-col gap-4 border-b border-white/[0.06] pb-6 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2 text-purple-300">
            <ChartNoAxesCombined className="h-4 w-4" />

            <span className="text-xs font-medium uppercase tracking-[0.16em]">
              Fundamental analysis
            </span>
          </div>

          <h3 className="mt-2 text-xl font-semibold text-white">
            Financial health and valuation
          </h3>

          <p className="mt-1 text-sm text-slate-500">
            Based on {latest_statement.fiscal_year} simulated financial
            statements.
          </p>
        </div>

        <div className="rounded-xl border border-amber-400/20 bg-amber-400/[0.07] px-3 py-2 text-xs text-amber-300">
          {fundamentals.data_status} data
        </div>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <RatioCard
          title="Earnings per share"
          value={formatCurrency(ratios.earnings_per_share)}
          description="Profit attributable to each outstanding share."
          icon={BadgeIndianRupee}
          accent="emerald"
        />

        <RatioCard
          title="Price to earnings"
          value={formatRatio(ratios.price_to_earnings)}
          description="Market price relative to annual earnings per share."
          icon={TrendingUp}
          accent="cyan"
        />

        <RatioCard
          title="Price to book"
          value={formatRatio(ratios.price_to_book)}
          description="Market price relative to accounting book value."
          icon={BookOpen}
          accent="purple"
        />

        <RatioCard
          title="Return on equity"
          value={formatPercent(ratios.return_on_equity_percent)}
          description="Profit generated from shareholder equity."
          icon={Activity}
          accent="emerald"
        />

        <RatioCard
          title="ROCE"
          value={formatPercent(ratios.return_on_capital_employed_percent)}
          description="Operating return generated from employed capital."
          icon={CircleGauge}
          accent="cyan"
        />

        <RatioCard
          title="Net profit margin"
          value={formatPercent(ratios.net_profit_margin_percent)}
          description="Percentage of revenue retained as net income."
          icon={Percent}
          accent="emerald"
        />

        <RatioCard
          title="Revenue growth"
          value={
            ratios.revenue_growth_percent
              ? formatPercent(ratios.revenue_growth_percent)
              : "N/A"
          }
          description="Year-over-year change in reported revenue."
          icon={Banknote}
          accent="amber"
        />

        <RatioCard
          title="Debt to equity"
          value={formatRatio(ratios.debt_to_equity)}
          description="Debt relative to shareholder equity."
          icon={Scale}
          accent="amber"
        />

        <RatioCard
          title="Current ratio"
          value={formatRatio(ratios.current_ratio)}
          description="Current assets available against short-term liabilities."
          icon={WalletCards}
          accent="purple"
        />
      </div>

      <div className="mt-6">
        <FinancialComparisonChart
          latest={latest_statement}
          previous={previous_statement}
        />
      </div>

      <p className="mt-5 text-xs leading-5 text-slate-600">
        Ratios are derived from deterministic simulated statements and are
        intended for software demonstration, not investment decisions.
      </p>
    </section>
  );
}
