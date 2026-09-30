import {
  BadgeIndianRupee,
  CircleDollarSign,
  ReceiptText,
  TrendingDown,
  TrendingUp,
} from "lucide-react";

import { formatCurrency } from "../../../features/market/market-utils";

import type { PortfolioSummary } from "../types";

interface PerformanceBreakdownProps {
  summary: PortfolioSummary;
}

export function PerformanceBreakdown({
  summary,
}: PerformanceBreakdownProps) {
  const totalPositive =
    Number(summary.total_pnl) >= 0;

  return (
    <section className="rounded-[28px] border border-white/[0.08] bg-[#10141f]/85 p-6">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-400/10 text-emerald-300">
          <CircleDollarSign className="h-5 w-5" />
        </div>

        <div>
          <h2 className="font-semibold text-white">
            Performance breakdown
          </h2>

          <p className="mt-1 text-xs text-slate-500">
            Fees-inclusive portfolio returns
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-3 sm:grid-cols-2">
        <PnlItem
          label="Realized P&L"
          value={summary.realized_pnl}
          icon={BadgeIndianRupee}
        />

        <PnlItem
          label="Unrealized P&L"
          value={summary.unrealized_pnl}
          icon={
            Number(summary.unrealized_pnl) >= 0
              ? TrendingUp
              : TrendingDown
          }
        />

        <PnlItem
          label="Total fees"
          value={`-${summary.total_fees}`}
          icon={ReceiptText}
          forceNegative
        />

        <div
          className={`rounded-2xl border p-4 ${
            totalPositive
              ? "border-emerald-400/20 bg-emerald-400/[0.06]"
              : "border-red-400/20 bg-red-400/[0.06]"
          }`}
        >
          <p className="text-xs text-slate-500">
            Total return
          </p>

          <p
            className={`mt-2 text-xl font-semibold ${
              totalPositive
                ? "text-emerald-300"
                : "text-red-300"
            }`}
          >
            {totalPositive ? "+" : ""}
            {Number(
              summary.total_return_percent,
            ).toFixed(2)}
            %
          </p>

          <p className="mt-1 text-xs text-slate-600">
            {formatCurrency(summary.total_pnl)}
          </p>
        </div>
      </div>
    </section>
  );
}

interface PnlItemProps {
  label: string;
  value: string;
  icon: typeof CircleDollarSign;
  forceNegative?: boolean;
}

function PnlItem({
  label,
  value,
  icon: Icon,
  forceNegative = false,
}: PnlItemProps) {
  const positive =
    !forceNegative && Number(value) >= 0;

  return (
    <div className="rounded-2xl border border-white/[0.07] bg-black/20 p-4">
      <div className="flex items-center gap-2 text-xs text-slate-500">
        <Icon className="h-4 w-4" />
        {label}
      </div>

      <p
        className={`mt-3 text-lg font-semibold ${
          positive
            ? "text-emerald-300"
            : "text-red-300"
        }`}
      >
        {positive && Number(value) > 0 ? "+" : ""}
        {formatCurrency(value)}
      </p>
    </div>
  );
}