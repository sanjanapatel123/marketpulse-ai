"use client";

import { AnalysisHeader } from "../../../features/analysis/components/analysis-header";
import { FundamentalsPanel } from "./fundamentals-panel";
import { useMarketData } from "../hooks/use-market-data";
import { MarketError } from "./market-error";
import { MarketLoading } from "./market-loading";
import { PriceChart } from "./price-chart";
import { QuoteOverview } from "./quote-overview";
import { StockSelector } from "./stock-selector";

export function MarketDashboard() {
  const {
    stocks,
    selectedSymbol,
    range,
    quote,
    candles,
    fundamentals,
    loading,
    error,
    setSelectedSymbol,
    setRange,
    retry,
  } = useMarketData();

  return (
    <div className="min-h-screen bg-[#080b12] text-white">
      <AnalysisHeader />

      <main className="relative overflow-hidden px-5 py-8 lg:px-8">
        <div className="pointer-events-none absolute left-1/4 top-0 h-[420px] w-[420px] rounded-full bg-emerald-500/[0.06] blur-[130px]" />

        <div className="relative mx-auto max-w-[1440px]">
          <div className="mb-7">
            <p className="text-xs font-medium uppercase tracking-[0.18em] text-emerald-300">
              Equity markets
            </p>

            <h1 className="mt-2 text-3xl font-semibold tracking-tight">
              Market overview
            </h1>

            <p className="mt-2 text-sm text-slate-500">
              Explore simulated NSE quotes and historical performance.
            </p>
          </div>

          <StockSelector
            stocks={stocks}
            symbol={selectedSymbol}
            range={range}
            onSymbolChange={setSelectedSymbol}
            onRangeChange={setRange}
          />

          <div className="mt-6">
            {loading && <MarketLoading />}

            {!loading && error && (
              <MarketError message={error} onRetry={retry} />
            )}

            {!loading &&
              !error &&
              quote &&
              fundamentals &&
              candles.length > 0 && (
                <div className="space-y-6">
                  <QuoteOverview quote={quote} />

                  <PriceChart candles={candles} currency={quote.currency} />

                  <FundamentalsPanel fundamentals={fundamentals} />
                </div>
              )}
          </div>
        </div>
      </main>
    </div>
  );
}
