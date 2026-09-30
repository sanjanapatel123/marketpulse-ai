import type { PriceAlert } from "../types/watchlist";

import { formatCurrency, formatDateTime } from "../utils/watchlist-formatters";

interface AlertActivityPanelProps {
  alerts: PriceAlert[];
}

export function AlertActivityPanel({ alerts }: AlertActivityPanelProps) {
  const sortedAlerts = [...alerts].sort(
    (first, second) =>
      new Date(second.created_at).getTime() -
      new Date(first.created_at).getTime(),
  );

  return (
    <section className="overflow-hidden rounded-2xl border border-white/10 bg-slate-950/70 backdrop-blur-xl">
      <div className="border-b border-white/10 px-5 py-5">
        <h2 className="text-lg font-semibold text-white">
          Price alert activity
        </h2>

        <p className="mt-1 text-sm text-slate-500">
          Automatically evaluated market thresholds
        </p>
      </div>

      {sortedAlerts.length === 0 ? (
        <div className="flex min-h-64 flex-col items-center justify-center px-6 text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-cyan-400/20 bg-cyan-400/10 text-xl">
            ◉
          </div>

          <h3 className="mt-4 font-semibold text-white">No price alerts</h3>

          <p className="mt-2 max-w-xs text-sm leading-6 text-slate-500">
            Select “Set alert” beside an equity to create an automatically
            monitored threshold.
          </p>
        </div>
      ) : (
        <div className="max-h-[620px] space-y-3 overflow-y-auto p-4">
          {sortedAlerts.map((alert) => (
            <AlertCard key={alert.id} alert={alert} />
          ))}
        </div>
      )}
    </section>
  );
}

function AlertCard({ alert }: { alert: PriceAlert }) {
  const isTriggered = alert.status === "TRIGGERED";

  const conditionLabel =
    alert.condition === "PRICE_ABOVE" ? "moves above" : "moves below";

  return (
    <article
      className={
        isTriggered
          ? "rounded-xl border border-amber-400/20 bg-amber-400/[0.07] p-4"
          : "rounded-xl border border-cyan-400/15 bg-cyan-400/[0.05] p-4"
      }
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <p className="font-semibold text-white">{alert.symbol}</p>

            <AlertStatusBadge status={alert.status} />
          </div>

          <p className="mt-2 text-sm text-slate-400">
            Price {conditionLabel}{" "}
            <span className="font-mono font-medium text-slate-200">
              {formatCurrency(alert.threshold, alert.currency)}
            </span>
          </p>
        </div>

        <div
          className={
            isTriggered
              ? "h-2.5 w-2.5 rounded-full bg-amber-400 shadow-lg shadow-amber-400/50"
              : "h-2.5 w-2.5 animate-pulse rounded-full bg-cyan-400 shadow-lg shadow-cyan-400/50"
          }
        />
      </div>

      {isTriggered && alert.triggered_price && (
        <div className="mt-4 grid grid-cols-2 gap-3 rounded-lg border border-white/5 bg-slate-950/40 p-3">
          <div>
            <p className="text-[10px] uppercase tracking-wider text-slate-600">
              Triggered price
            </p>

            <p className="mt-1 font-mono text-sm font-medium text-amber-200">
              {formatCurrency(alert.triggered_price, alert.currency)}
            </p>
          </div>

          <div>
            <p className="text-[10px] uppercase tracking-wider text-slate-600">
              Triggered at
            </p>

            <p className="mt-1 text-xs text-slate-300">
              {formatDateTime(alert.triggered_at)}
            </p>
          </div>
        </div>
      )}

      {!isTriggered && (
        <p className="mt-4 text-xs text-slate-600">
          Monitoring since {formatDateTime(alert.created_at)}
        </p>
      )}
    </article>
  );
}

function AlertStatusBadge({ status }: { status: PriceAlert["status"] }) {
  const styles = {
    ACTIVE: "border-cyan-400/20 bg-cyan-400/10 text-cyan-200",
    TRIGGERED: "border-amber-400/20 bg-amber-400/10 text-amber-200",
    DISABLED: "border-slate-400/20 bg-slate-400/10 text-slate-400",
  };

  return (
    <span
      className={`rounded-full border px-2 py-0.5 text-[10px] font-semibold tracking-wider ${styles[status]}`}
    >
      {status}
    </span>
  );
}
