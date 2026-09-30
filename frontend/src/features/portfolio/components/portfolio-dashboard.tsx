"use client";

import { AnalysisHeader } from "../../analysis/components/analysis-header";

import { usePortfolio } from "../hooks/use-portfolio";
import { PortfolioMetrics } from "./portfolio-metrics";
import { PortfolioSelector } from "./portfolio-selector";
import { PositionsTable } from "./positions-table";
import { TradeTicket } from "./trade-ticket";
import { AllocationChart } from "./allocation-chart";
import { PerformanceBreakdown } from "./performance-breakdown";
import { TransactionHistory } from "./transaction-history";
import { RiskDashboard } from "./risk-dashboard";

export function PortfolioDashboard() {
  const {
    portfolios,
    selectedPortfolioId,
    summary,
    risk,
    transactions,
    loading,
    submittingTrade,
    error,
    setSelectedPortfolioId,
    submitTrade,
    retry,
  } = usePortfolio();

  return (
    <div className="min-h-screen bg-[#080b12] text-white">
      <AnalysisHeader />

      <main className="mx-auto max-w-[1440px] px-5 py-8 lg:px-8">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-emerald-300">
              Paper portfolio
            </p>

            <h1 className="mt-2 text-3xl font-semibold">
              Portfolio intelligence
            </h1>

            <p className="mt-2 text-sm text-slate-500">
              Track holdings, cash and fees-inclusive P&L.
            </p>
          </div>

          <PortfolioSelector
            portfolios={portfolios}
            selectedId={selectedPortfolioId}
            onChange={setSelectedPortfolioId}
          />
        </div>

        {error && (
          <div className="mt-6 rounded-xl border border-red-400/20 bg-red-400/[0.06] p-4 text-sm text-red-300">
            {error}

            <button
              type="button"
              onClick={() => void retry()}
              className="ml-3 underline"
            >
              Retry
            </button>
          </div>
        )}

        {loading && (
          <div className="mt-6 h-64 animate-pulse rounded-[28px] bg-white/[0.04]" />
        )}

        {!loading && summary && risk && (
          <div className="mt-6 space-y-6">
            <PortfolioMetrics summary={summary} />

            <div className="grid gap-6 xl:grid-cols-2">
              <PerformanceBreakdown summary={summary} />

              <AllocationChart summary={summary} />
            </div>

            <RiskDashboard risk={risk} />

            <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_340px]">
              <PositionsTable positions={summary.positions} />

              <TradeTicket
                submitting={submittingTrade}
                onSubmit={submitTrade}
              />
            </div>

            <TransactionHistory transactions={transactions} />
          </div>
        )}
      </main>
    </div>
  );
}
