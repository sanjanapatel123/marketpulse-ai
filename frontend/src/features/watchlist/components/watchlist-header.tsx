interface WatchlistHeaderProps {
  activeAlertCount: number;
  triggeredAlertCount: number;
  onRefresh: () => Promise<void>;
  isRefreshing: boolean;
}

export function WatchlistHeader({
  activeAlertCount,
  triggeredAlertCount,
  onRefresh,
  isRefreshing,
}: WatchlistHeaderProps) {
  return (
    <header className="relative overflow-hidden rounded-3xl border border-white/10 bg-slate-950 px-6 py-7 shadow-2xl shadow-emerald-950/20 sm:px-8">
      <div className="absolute -right-24 -top-24 h-64 w-64 rounded-full bg-emerald-500/10 blur-3xl" />
      <div className="absolute -bottom-32 left-1/3 h-64 w-64 rounded-full bg-cyan-500/10 blur-3xl" />

      <div className="relative flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <div className="mb-3 flex items-center gap-2">
            <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />

            <span className="text-xs font-semibold uppercase tracking-[0.22em] text-emerald-300">
              Market intelligence
            </span>
          </div>

          <h1 className="text-3xl font-semibold tracking-tight text-white sm:text-4xl">
            Smart Watchlists
          </h1>

          <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-400 sm:text-base">
            Track Indian equities, monitor deterministic market prices and
            receive automatically evaluated price alerts.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <HeaderMetric
            label="Active alerts"
            value={activeAlertCount}
            tone="active"
          />

          <HeaderMetric
            label="Triggered"
            value={triggeredAlertCount}
            tone="triggered"
          />

          <button
            type="button"
            onClick={() => void onRefresh()}
            disabled={isRefreshing}
            className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-medium text-slate-200 transition hover:border-emerald-400/40 hover:bg-emerald-400/10 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isRefreshing ? "Refreshing..." : "Refresh data"}
          </button>
        </div>
      </div>
    </header>
  );
}

interface HeaderMetricProps {
  label: string;
  value: number;
  tone: "active" | "triggered";
}

function HeaderMetric({ label, value, tone }: HeaderMetricProps) {
  const toneClasses =
    tone === "triggered"
      ? "border-amber-400/20 bg-amber-400/10 text-amber-200"
      : "border-cyan-400/20 bg-cyan-400/10 text-cyan-200";

  return (
    <div className={`min-w-28 rounded-xl border px-4 py-2.5 ${toneClasses}`}>
      <p className="text-[11px] uppercase tracking-wider opacity-70">{label}</p>

      <p className="mt-1 text-xl font-semibold">{value}</p>
    </div>
  );
}
