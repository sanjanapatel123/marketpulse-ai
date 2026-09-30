"use client";

import { useMemo, useState } from "react";

import { useWatchlists } from "../hooks/use-watchlists";

import type { WatchlistItemQuote } from "../types/watchlist";

import { AddStockDialog } from "./add-stock-dialog";
import { AlertActivityPanel } from "./alert-activity-panel";
import { CreateAlertDialog } from "./create-alert-dialog";
import { CreateWatchlistDialog } from "./create-watchlist-dialog";
import { WatchlistHeader } from "./watchlist-header";
import { WatchlistSelector } from "./watchlist-selector";
import { WatchlistStockTable } from "./watchlist-stock-table";

export function WatchlistWorkspace() {
  const {
    watchlists,
    selectedWatchlistId,
    detail,
    isLoadingWatchlists,
    isLoadingDetail,
    isSubmitting,
    error,
    selectWatchlist,
    createWatchlist,
    addItem,
    removeItem,
    createAlert,
    refresh,
    clearError,
  } = useWatchlists();

  const [isCreateWatchlistOpen, setIsCreateWatchlistOpen] = useState(false);

  const [isAddStockOpen, setIsAddStockOpen] = useState(false);

  const [selectedAlertItem, setSelectedAlertItem] =
    useState<WatchlistItemQuote | null>(null);

  const alerts = detail?.alerts ?? [];
  const items = detail?.items ?? [];

  const activeAlertCount = useMemo(
    () => alerts.filter((alert) => alert.status === "ACTIVE").length,
    [alerts],
  );

  const triggeredAlertCount = useMemo(
    () => alerts.filter((alert) => alert.status === "TRIGGERED").length,
    [alerts],
  );

  const existingSymbols = useMemo(
    () => items.map((item) => item.item.symbol),
    [items],
  );

  async function handleRemoveItem(symbol: string): Promise<void> {
    const shouldRemove = window.confirm(
      `Remove ${symbol} from this watchlist?`,
    );

    if (!shouldRemove) {
      return;
    }

    await removeItem(symbol);
  }

  function closeAlertDialog() {
    setSelectedAlertItem(null);
  }

  return (
    <main className="min-h-screen bg-[#050a12] text-slate-100">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_top_left,rgba(16,185,129,0.08),transparent_32%),radial-gradient(circle_at_bottom_right,rgba(34,211,238,0.06),transparent_30%)]" />

      <div className="relative mx-auto max-w-7xl space-y-6 px-4 py-8 sm:px-6 lg:px-8">
        <WatchlistHeader
          activeAlertCount={activeAlertCount}
          triggeredAlertCount={triggeredAlertCount}
          onRefresh={refresh}
          isRefreshing={isLoadingDetail}
        />

        {error && <ErrorBanner message={error} onClose={clearError} />}

        <WatchlistSelector
          watchlists={watchlists}
          selectedId={selectedWatchlistId}
          onSelect={selectWatchlist}
          onCreateClick={() => setIsCreateWatchlistOpen(true)}
          isLoading={isLoadingWatchlists}
        />

        {isLoadingDetail ? (
          <WatchlistLoadingState />
        ) : detail ? (
          <>
            <section className="rounded-2xl border border-white/10 bg-gradient-to-r from-slate-950 to-slate-900/80 px-5 py-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="text-xs uppercase tracking-[0.16em] text-slate-600">
                    Current portfolio lens
                  </p>

                  <h2 className="mt-1 text-xl font-semibold text-white">
                    {detail.watchlist.name}
                  </h2>
                </div>

                <div className="flex items-center gap-2 text-xs text-slate-500">
                  <span className="h-2 w-2 rounded-full bg-emerald-400" />
                  Auto-refresh every 10 seconds
                </div>
              </div>
            </section>

            <div className="grid gap-6 xl:grid-cols-[minmax(0,1.7fr)_minmax(320px,0.8fr)]">
              <WatchlistStockTable
                items={items}
                isSubmitting={isSubmitting}
                onAddStockClick={() => setIsAddStockOpen(true)}
                onCreateAlertClick={setSelectedAlertItem}
                onRemove={handleRemoveItem}
              />

              <AlertActivityPanel alerts={alerts} />
            </div>
          </>
        ) : (
          <EmptyWatchlistState
            onCreate={() => setIsCreateWatchlistOpen(true)}
          />
        )}
      </div>

      <CreateWatchlistDialog
        isOpen={isCreateWatchlistOpen}
        isSubmitting={isSubmitting}
        onClose={() => setIsCreateWatchlistOpen(false)}
        onSubmit={createWatchlist}
      />

      <AddStockDialog
        isOpen={isAddStockOpen}
        isSubmitting={isSubmitting}
        existingSymbols={existingSymbols}
        onClose={() => setIsAddStockOpen(false)}
        onSubmit={addItem}
      />

      <CreateAlertDialog
        isOpen={selectedAlertItem !== null}
        selectedItem={selectedAlertItem}
        isSubmitting={isSubmitting}
        onClose={closeAlertDialog}
        onSubmit={createAlert}
      />
    </main>
  );
}

interface ErrorBannerProps {
  message: string;
  onClose: () => void;
}

function ErrorBanner({ message, onClose }: ErrorBannerProps) {
  return (
    <div className="flex items-start justify-between gap-4 rounded-2xl border border-rose-400/20 bg-rose-400/10 px-5 py-4 text-sm text-rose-100">
      <p>{message}</p>

      <button
        type="button"
        onClick={onClose}
        className="text-rose-200/70 transition hover:text-white"
      >
        ×
      </button>
    </div>
  );
}

function WatchlistLoadingState() {
  return (
    <div className="grid animate-pulse gap-6 xl:grid-cols-[minmax(0,1.7fr)_minmax(320px,0.8fr)]">
      <div className="h-96 rounded-2xl border border-white/5 bg-white/[0.03]" />
      <div className="h-96 rounded-2xl border border-white/5 bg-white/[0.03]" />
    </div>
  );
}

function EmptyWatchlistState({ onCreate }: { onCreate: () => void }) {
  return (
    <section className="flex min-h-96 flex-col items-center justify-center rounded-3xl border border-dashed border-white/10 bg-slate-950/50 px-6 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl border border-emerald-400/20 bg-emerald-400/10 text-2xl text-emerald-200">
        +
      </div>

      <h2 className="mt-6 text-xl font-semibold text-white">
        Create your first watchlist
      </h2>

      <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
        Organize equities, observe deterministic market prices and configure
        automatically evaluated alerts.
      </p>

      <button
        type="button"
        onClick={onCreate}
        className="mt-6 rounded-xl bg-gradient-to-r from-emerald-400 to-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950"
      >
        Create watchlist
      </button>
    </section>
  );
}
