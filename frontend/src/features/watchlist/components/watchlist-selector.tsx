import type { Watchlist } from "../types/watchlist";

interface WatchlistSelectorProps {
  watchlists: Watchlist[];
  selectedId: string | null;
  onSelect: (watchlistId: string) => void;
  onCreateClick: () => void;
  isLoading: boolean;
}

export function WatchlistSelector({
  watchlists,
  selectedId,
  onSelect,
  onCreateClick,
  isLoading,
}: WatchlistSelectorProps) {
  return (
    <section className="rounded-2xl border border-white/10 bg-slate-950/70 p-4 backdrop-blur-xl">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div className="w-full sm:max-w-md">
          <label
            htmlFor="watchlist-selector"
            className="mb-2 block text-xs font-semibold uppercase tracking-[0.16em] text-slate-500"
          >
            Selected watchlist
          </label>

          <select
            id="watchlist-selector"
            value={selectedId ?? ""}
            onChange={(event) => onSelect(event.target.value)}
            disabled={isLoading || watchlists.length === 0}
            className="h-12 w-full rounded-xl border border-white/10 bg-slate-900 px-4 text-sm text-slate-100 outline-none transition focus:border-emerald-400/60 focus:ring-4 focus:ring-emerald-400/10 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {watchlists.length === 0 && (
              <option value="">No watchlist available</option>
            )}

            {watchlists.map((watchlist) => (
              <option key={watchlist.id} value={watchlist.id}>
                {watchlist.name}
              </option>
            ))}
          </select>
        </div>

        <button
          type="button"
          onClick={onCreateClick}
          className="h-12 rounded-xl bg-gradient-to-r from-emerald-400 to-cyan-400 px-5 text-sm font-semibold text-slate-950 shadow-lg shadow-emerald-950/30 transition hover:brightness-110 active:scale-[0.98]"
        >
          + New watchlist
        </button>
      </div>
    </section>
  );
}
