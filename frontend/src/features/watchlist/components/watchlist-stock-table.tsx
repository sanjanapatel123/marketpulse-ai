import type { WatchlistItemQuote } from "../types/watchlist";

import { formatCurrency, formatPercent } from "../utils/watchlist-formatters";

interface WatchlistStockTableProps {
  items: WatchlistItemQuote[];
  isSubmitting: boolean;
  onAddStockClick: () => void;
  onCreateAlertClick: (item: WatchlistItemQuote) => void;
  onRemove: (symbol: string) => Promise<void>;
}

export function WatchlistStockTable({
  items,
  isSubmitting,
  onAddStockClick,
  onCreateAlertClick,
  onRemove,
}: WatchlistStockTableProps) {
  return (
    <section className="overflow-hidden rounded-2xl border border-white/10 bg-slate-950/70 backdrop-blur-xl">
      <div className="flex flex-col gap-4 border-b border-white/10 px-5 py-5 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-white">Tracked equities</h2>

          <p className="mt-1 text-sm text-slate-500">
            {items.length} {items.length === 1 ? "company" : "companies"}{" "}
            currently monitored
          </p>
        </div>

        <button
          type="button"
          onClick={onAddStockClick}
          className="rounded-xl border border-emerald-400/30 bg-emerald-400/10 px-4 py-2.5 text-sm font-medium text-emerald-200 transition hover:bg-emerald-400/20"
        >
          + Add equity
        </button>
      </div>

      {items.length === 0 ? (
        <EmptyStockState onAddStockClick={onAddStockClick} />
      ) : (
        <>
          <div className="hidden overflow-x-auto md:block">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-white/5 text-xs uppercase tracking-wider text-slate-500">
                  <th className="px-5 py-4 font-medium">Company</th>
                  <th className="px-5 py-4 font-medium">Price</th>
                  <th className="px-5 py-4 font-medium">Change</th>
                  <th className="px-5 py-4 font-medium">Sector</th>
                  <th className="px-5 py-4 text-right font-medium">Actions</th>
                </tr>
              </thead>

              <tbody>
                {items.map((item) => (
                  <StockTableRow
                    key={item.item.id}
                    item={item}
                    isSubmitting={isSubmitting}
                    onCreateAlertClick={onCreateAlertClick}
                    onRemove={onRemove}
                  />
                ))}
              </tbody>
            </table>
          </div>

          <div className="grid gap-3 p-4 md:hidden">
            {items.map((item) => (
              <StockMobileCard
                key={item.item.id}
                item={item}
                isSubmitting={isSubmitting}
                onCreateAlertClick={onCreateAlertClick}
                onRemove={onRemove}
              />
            ))}
          </div>
        </>
      )}
    </section>
  );
}

interface StockRowProps {
  item: WatchlistItemQuote;
  isSubmitting: boolean;
  onCreateAlertClick: (item: WatchlistItemQuote) => void;
  onRemove: (symbol: string) => Promise<void>;
}

function StockTableRow({
  item,
  isSubmitting,
  onCreateAlertClick,
  onRemove,
}: StockRowProps) {
  const change = Number(item.change_percent);
  const isPositive = change >= 0;

  return (
    <tr className="border-b border-white/5 transition last:border-0 hover:bg-white/[0.025]">
      <td className="px-5 py-5">
        <CompanyIdentity item={item} />
      </td>

      <td className="px-5 py-5">
        <p className="font-mono font-medium text-slate-100">
          {formatCurrency(item.price, item.currency)}
        </p>

        <p className="mt-1 text-xs text-slate-600">{item.data_status}</p>
      </td>

      <td className="px-5 py-5">
        <span className={isPositive ? "text-emerald-300" : "text-rose-300"}>
          {formatPercent(item.change_percent)}
        </span>

        <p className="mt-1 text-xs text-slate-500">
          {formatCurrency(item.change, item.currency)}
        </p>
      </td>

      <td className="px-5 py-5 text-sm text-slate-400">{item.sector}</td>

      <td className="px-5 py-5">
        <StockActions
          item={item}
          isSubmitting={isSubmitting}
          onCreateAlertClick={onCreateAlertClick}
          onRemove={onRemove}
        />
      </td>
    </tr>
  );
}

function StockMobileCard({
  item,
  isSubmitting,
  onCreateAlertClick,
  onRemove,
}: StockRowProps) {
  const isPositive = Number(item.change_percent) >= 0;

  return (
    <article className="rounded-xl border border-white/10 bg-slate-900/70 p-4">
      <CompanyIdentity item={item} />

      <div className="mt-5 flex items-end justify-between">
        <div>
          <p className="text-xs text-slate-500">Market price</p>

          <p className="mt-1 font-mono text-lg font-semibold text-white">
            {formatCurrency(item.price, item.currency)}
          </p>
        </div>

        <p
          className={
            isPositive
              ? "text-sm font-medium text-emerald-300"
              : "text-sm font-medium text-rose-300"
          }
        >
          {formatPercent(item.change_percent)}
        </p>
      </div>

      <div className="mt-4">
        <StockActions
          item={item}
          isSubmitting={isSubmitting}
          onCreateAlertClick={onCreateAlertClick}
          onRemove={onRemove}
        />
      </div>
    </article>
  );
}

function CompanyIdentity({ item }: { item: WatchlistItemQuote }) {
  return (
    <div className="flex items-center gap-3">
      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-400/20 to-cyan-400/20 text-sm font-bold text-emerald-200">
        {item.item.symbol.slice(0, 2)}
      </div>

      <div>
        <p className="font-semibold text-slate-100">{item.item.symbol}</p>

        <p className="mt-0.5 max-w-52 truncate text-xs text-slate-500">
          {item.company_name}
        </p>
      </div>
    </div>
  );
}

function StockActions({
  item,
  isSubmitting,
  onCreateAlertClick,
  onRemove,
}: StockRowProps) {
  return (
    <div className="flex justify-end gap-2">
      <button
        type="button"
        onClick={() => onCreateAlertClick(item)}
        disabled={isSubmitting}
        className="rounded-lg border border-cyan-400/20 bg-cyan-400/10 px-3 py-2 text-xs font-medium text-cyan-200 transition hover:bg-cyan-400/20 disabled:opacity-50"
      >
        Set alert
      </button>

      <button
        type="button"
        onClick={() => void onRemove(item.item.symbol)}
        disabled={isSubmitting}
        className="rounded-lg border border-rose-400/20 bg-rose-400/10 px-3 py-2 text-xs font-medium text-rose-200 transition hover:bg-rose-400/20 disabled:opacity-50"
      >
        Remove
      </button>
    </div>
  );
}

function EmptyStockState({ onAddStockClick }: { onAddStockClick: () => void }) {
  return (
    <div className="flex min-h-72 flex-col items-center justify-center px-6 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-emerald-400/20 bg-emerald-400/10 text-2xl">
        ↗
      </div>

      <h3 className="mt-5 text-lg font-semibold text-white">
        Start tracking equities
      </h3>

      <p className="mt-2 max-w-sm text-sm leading-6 text-slate-500">
        Add NSE-listed companies to monitor market prices and configure
        automatic threshold alerts.
      </p>

      <button
        type="button"
        onClick={onAddStockClick}
        className="mt-5 rounded-xl bg-emerald-400 px-4 py-2.5 text-sm font-semibold text-slate-950"
      >
        Add first equity
      </button>
    </div>
  );
}
