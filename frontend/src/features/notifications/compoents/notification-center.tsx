"use client";

import { useEffect, useMemo, useState } from "react";

import { useNotificationStream } from "../hooks/use-notification-stream";

import type {
  NotificationConnectionState,
  NotificationEvent,
} from "../types/notification";

const SEEN_CURSOR_KEY = "marketpulse.notification-seen-cursor";

export function NotificationCenter() {
  const {
    notifications,
    latestLiveNotification,
    connectionState,
    isLoadingHistory,
    error,
    retry,
    resetCursorAndReconnect,
  } = useNotificationStream();

  const [isOpen, setIsOpen] = useState(false);
  const [seenCursor, setSeenCursor] = useState(0);

  const [toastNotification, setToastNotification] =
    useState<NotificationEvent | null>(null);

  useEffect(() => {
    const stored = Number(window.localStorage.getItem(SEEN_CURSOR_KEY) ?? "0");

    if (Number.isInteger(stored) && stored >= 0) {
      setSeenCursor(stored);
    }
  }, []);

  useEffect(() => {
    if (!latestLiveNotification) {
      return;
    }

    setToastNotification(latestLiveNotification);

    const timeoutId = window.setTimeout(() => {
      setToastNotification(null);
    }, 5_000);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [latestLiveNotification]);

  const unreadCount = useMemo(
    () =>
      notifications.filter((notification) => notification.sequence > seenCursor)
        .length,
    [notifications, seenCursor],
  );

  function openDrawer() {
    setIsOpen(true);

    const latestSequence = notifications[0]?.sequence ?? seenCursor;

    setSeenCursor(latestSequence);

    window.localStorage.setItem(SEEN_CURSOR_KEY, String(latestSequence));
  }

  return (
    <>
      <button
        type="button"
        onClick={openDrawer}
        aria-label="Open notifications"
        className="fixed right-5 top-5 z-40 flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-slate-950/90 text-slate-300 shadow-2xl shadow-black/30 backdrop-blur-xl transition hover:border-emerald-400/30 hover:text-white"
      >
        <BellIcon />

        {unreadCount > 0 && (
          <span className="absolute -right-1.5 -top-1.5 flex min-h-5 min-w-5 items-center justify-center rounded-full bg-rose-500 px-1 text-[10px] font-bold text-white ring-2 ring-slate-950">
            {unreadCount > 99 ? "99+" : unreadCount}
          </span>
        )}

        <ConnectionDot state={connectionState} />
      </button>

      {toastNotification && (
        <NotificationToast
          notification={toastNotification}
          onClose={() => setToastNotification(null)}
          onOpen={() => {
            setToastNotification(null);
            openDrawer();
          }}
        />
      )}

      {isOpen && (
        <NotificationDrawer
          notifications={notifications}
          connectionState={connectionState}
          isLoading={isLoadingHistory}
          error={error}
          onClose={() => setIsOpen(false)}
          onRetry={retry}
          onReset={resetCursorAndReconnect}
        />
      )}
    </>
  );
}

function ConnectionDot({ state }: { state: NotificationConnectionState }) {
  const styles = {
    connected: "bg-emerald-400 shadow-emerald-400/50",
    reconnecting: "animate-pulse bg-amber-400 shadow-amber-400/50",
    disconnected: "bg-rose-400 shadow-rose-400/50",
  };

  return (
    <span
      className={`absolute bottom-1 right-1 h-2.5 w-2.5 rounded-full shadow-lg ring-2 ring-slate-950 ${styles[state]}`}
    />
  );
}

interface NotificationDrawerProps {
  notifications: NotificationEvent[];
  connectionState: NotificationConnectionState;
  isLoading: boolean;
  error: string | null;
  onClose: () => void;
  onRetry: () => void;
  onReset: () => void;
}

function NotificationDrawer({
  notifications,
  connectionState,
  isLoading,
  error,
  onClose,
  onRetry,
  onReset,
}: NotificationDrawerProps) {
  return (
    <div className="fixed inset-0 z-50">
      <button
        type="button"
        aria-label="Close notifications"
        onClick={onClose}
        className="absolute inset-0 bg-slate-950/70 backdrop-blur-sm"
      />

      <aside className="absolute right-0 top-0 flex h-full w-full max-w-md flex-col border-l border-white/10 bg-[#07101c] shadow-2xl shadow-black/60">
        <header className="border-b border-white/10 px-5 py-5">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-emerald-300">
                MarketPulse
              </p>

              <h2 className="mt-1 text-xl font-semibold text-white">
                Notifications
              </h2>
            </div>

            <button
              type="button"
              onClick={onClose}
              className="flex h-9 w-9 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-slate-400 transition hover:bg-white/10 hover:text-white"
            >
              ×
            </button>
          </div>

          <div className="mt-4">
            <ConnectionBadge state={connectionState} />
          </div>
        </header>

        {error && (
          <div className="border-b border-rose-400/15 bg-rose-400/[0.07] px-5 py-4">
            <p className="text-sm text-rose-200">{error}</p>

            <div className="mt-3 flex gap-2">
              <button
                type="button"
                onClick={onRetry}
                className="rounded-lg bg-rose-400/15 px-3 py-2 text-xs font-medium text-rose-100"
              >
                Retry connection
              </button>

              <button
                type="button"
                onClick={onReset}
                className="rounded-lg border border-white/10 px-3 py-2 text-xs text-slate-300"
              >
                Reset cursor
              </button>
            </div>
          </div>
        )}

        <div className="flex-1 overflow-y-auto p-4">
          {isLoading ? (
            <NotificationSkeleton />
          ) : notifications.length === 0 ? (
            <EmptyNotifications />
          ) : (
            <div className="space-y-3">
              {notifications.map((notification) => (
                <NotificationCard
                  key={notification.id}
                  notification={notification}
                />
              ))}
            </div>
          )}
        </div>

        <footer className="border-t border-white/10 px-5 py-4">
          <p className="text-center text-xs text-slate-600">
            Durable SSE delivery with cursor-based replay
          </p>
        </footer>
      </aside>
    </div>
  );
}

function ConnectionBadge({ state }: { state: NotificationConnectionState }) {
  const config = {
    connected: {
      label: "Live connection",
      classes: "border-emerald-400/20 bg-emerald-400/10 text-emerald-200",
    },
    reconnecting: {
      label: "Reconnecting",
      classes: "border-amber-400/20 bg-amber-400/10 text-amber-200",
    },
    disconnected: {
      label: "Disconnected",
      classes: "border-rose-400/20 bg-rose-400/10 text-rose-200",
    },
  };

  const current = config[state];

  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-medium ${current.classes}`}
    >
      <span
        className={`h-1.5 w-1.5 rounded-full ${
          state === "connected"
            ? "bg-emerald-400"
            : state === "reconnecting"
              ? "animate-pulse bg-amber-400"
              : "bg-rose-400"
        }`}
      />

      {current.label}
    </span>
  );
}

function NotificationCard({
  notification,
}: {
  notification: NotificationEvent;
}) {
  return (
    <article className="rounded-2xl border border-white/10 bg-slate-950/60 p-4 transition hover:border-emerald-400/20">
      <div className="flex items-start gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-400/20 to-cyan-400/20 text-sm font-bold text-emerald-200">
          {notification.payload.symbol.slice(0, 2)}
        </div>

        <div className="min-w-0 flex-1">
          <p className="font-medium text-slate-100">
            {notification.payload.title}
          </p>

          <p className="mt-1.5 text-sm leading-6 text-slate-400">
            {notification.payload.message}
          </p>

          <div className="mt-3 flex items-center justify-between gap-3">
            <time className="text-xs text-slate-600">
              {formatNotificationTime(notification.created_at)}
            </time>

            <span className="font-mono text-[10px] text-slate-700">
              #{notification.sequence}
            </span>
          </div>
        </div>
      </div>
    </article>
  );
}

interface NotificationToastProps {
  notification: NotificationEvent;
  onClose: () => void;
  onOpen: () => void;
}

function NotificationToast({
  notification,
  onClose,
  onOpen,
}: NotificationToastProps) {
  return (
    <div className="fixed bottom-5 right-5 z-50 w-[calc(100%-2.5rem)] max-w-sm overflow-hidden rounded-2xl border border-emerald-400/20 bg-slate-950 shadow-2xl shadow-black/50">
      <div className="h-1 bg-gradient-to-r from-emerald-400 to-cyan-400" />

      <div className="p-4">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-emerald-300">
              Price alert
            </p>

            <p className="mt-2 font-semibold text-white">
              {notification.payload.title}
            </p>

            <p className="mt-1 text-sm leading-5 text-slate-400">
              {notification.payload.message}
            </p>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="text-slate-500 hover:text-white"
          >
            ×
          </button>
        </div>

        <button
          type="button"
          onClick={onOpen}
          className="mt-4 text-xs font-medium text-emerald-300 hover:text-emerald-200"
        >
          View notification →
        </button>
      </div>
    </div>
  );
}

function NotificationSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((item) => (
        <div
          key={item}
          className="h-32 animate-pulse rounded-2xl border border-white/5 bg-white/[0.03]"
        />
      ))}
    </div>
  );
}

function EmptyNotifications() {
  return (
    <div className="flex h-full min-h-80 flex-col items-center justify-center text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-emerald-400/20 bg-emerald-400/10">
        <BellIcon />
      </div>

      <h3 className="mt-5 font-semibold text-white">No notifications yet</h3>

      <p className="mt-2 max-w-xs text-sm leading-6 text-slate-500">
        Triggered watchlist alerts will appear here instantly.
      </p>
    </div>
  );
}

function BellIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      className="h-5 w-5"
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M15 17H9m9-2V11a6 6 0 1 0-12 0v4l-2 2h16l-2-2Zm-7 5h2"
      />
    </svg>
  );
}

function formatNotificationTime(value: string): string {
  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}
