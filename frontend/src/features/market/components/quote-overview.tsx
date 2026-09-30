import {
  ArrowDownRight,
  ArrowUpRight,
  BarChart3,
  Clock3,
  Gauge,
  IndianRupee,
} from "lucide-react";

import {
  formatCompactNumber,
  formatCurrency,
  formatDateTime,
} from "../market-utils";

import type { MarketQuote } from "../types";

interface QuoteOverviewProps {
  quote: MarketQuote;
}

export function QuoteOverview({
  quote,
}: QuoteOverviewProps) {
  const positive = Number(quote.change) >= 0;
  const ChangeIcon = positive
    ? ArrowUpRight
    : ArrowDownRight;

  return (
    <section className="rounded-[28px] border border-white/[0.08] bg-[#10141f]/85 p-6 shadow-2xl shadow-black/20 backdrop-blur-xl">
      <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <div className="flex items-center gap-3">
            <span className="rounded-lg bg-emerald-400/10 px-2.5 py-1 text-xs font-semibold text-emerald-300">
              {quote.exchange}
            </span>

            <span className="rounded-lg border border-amber-400/20 bg-amber-400/[0.07] px-2.5 py-1 text-xs text-amber-300">
              {quote.data_status}
            </span>
          </div>

          <h2 className="mt-4 text-3xl font-semibold tracking-tight text-white">
            {quote.symbol}
          </h2>

          <div className="mt-3 flex flex-wrap items-end gap-3">
            <p className="text-4xl font-semibold text-white">
              {formatCurrency(
                quote.price,
                quote.currency,
              )}
            </p>

            <div
              className={`mb-1 flex items-center gap-1 text-sm font-semibold ${
                positive
                  ? "text-emerald-300"
                  : "text-red-300"
              }`}
            >
              <ChangeIcon className="h-4 w-4" />

              {positive ? "+" : ""}
              {quote.change} ({positive ? "+" : ""}
              {quote.change_percent}%)
            </div>
          </div>

          <div className="mt-4 flex items-center gap-2 text-xs text-slate-500">
            <Clock3 className="h-3.5 w-3.5" />
            Updated {formatDateTime(quote.as_of)}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <QuoteMetric
            label="Open"
            value={formatCurrency(
              quote.open,
              quote.currency,
            )}
            icon={IndianRupee}
          />

          <QuoteMetric
            label="Day high"
            value={formatCurrency(
              quote.day_high,
              quote.currency,
            )}
            icon={ArrowUpRight}
          />

          <QuoteMetric
            label="Day low"
            value={formatCurrency(
              quote.day_low,
              quote.currency,
            )}
            icon={ArrowDownRight}
          />

          <QuoteMetric
            label="Volume"
            value={formatCompactNumber(quote.volume)}
            icon={BarChart3}
          />
        </div>
      </div>
    </section>
  );
}

interface QuoteMetricProps {
  label: string;
  value: string;
  icon: typeof Gauge;
}

function QuoteMetric({
  label,
  value,
  icon: Icon,
}: QuoteMetricProps) {
  return (
    <div className="min-w-[130px] rounded-2xl border border-white/[0.07] bg-black/20 p-4">
      <div className="flex items-center gap-2 text-slate-500">
        <Icon className="h-3.5 w-3.5" />
        <span className="text-xs">{label}</span>
      </div>

      <p className="mt-2 text-sm font-semibold text-slate-200">
        {value}
      </p>
    </div>
  );
}