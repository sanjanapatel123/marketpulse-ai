"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import {
  getNotificationHistory,
  NOTIFICATION_API_URL,
} from "../api/notification-api";

import {
  mergeNotifications,
  parseStoredCursor,
  shouldAcceptNotification,
} from "../utils/notification-state";

import type {
  NotificationConnectionState,
  NotificationEvent,
} from "../types/notification";

const CURSOR_STORAGE_KEY = "marketpulse.notification-cursor";

const INITIAL_RECONNECT_DELAY_MS = 1_000;
const MAX_RECONNECT_DELAY_MS = 15_000;
const MAX_RECONNECT_ATTEMPTS = 8;

function readStoredCursor(): number {
  if (typeof window === "undefined") {
    return 0;
  }

  return parseStoredCursor(window.localStorage.getItem(CURSOR_STORAGE_KEY));
}

export function useNotificationStream() {
  const [notifications, setNotifications] = useState<NotificationEvent[]>([]);

  const [latestLiveNotification, setLatestLiveNotification] =
    useState<NotificationEvent | null>(null);

  const [connectionState, setConnectionState] =
    useState<NotificationConnectionState>("disconnected");

  const [isLoadingHistory, setIsLoadingHistory] = useState(true);

  const [error, setError] = useState<string | null>(null);

  const eventSourceRef = useRef<EventSource | null>(null);

  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const cursorRef = useRef(0);
  const reconnectAttemptRef = useRef(0);
  const isMountedRef = useRef(false);

  const saveCursor = useCallback((cursor: number) => {
    cursorRef.current = cursor;

    window.localStorage.setItem(CURSOR_STORAGE_KEY, String(cursor));
  }, []);

  const handleNotificationEvent = useCallback(
    (messageEvent: MessageEvent<string>) => {
      try {
        const notification = JSON.parse(messageEvent.data) as NotificationEvent;

        if (!shouldAcceptNotification(notification, cursorRef.current)) {
          return;
        }

        setNotifications((current) =>
          mergeNotifications(current, [notification]),
        );

        saveCursor(notification.sequence);
        setError(null);
      } catch {
        setError("Received an invalid notification event");
      }
    },
    [saveCursor],
  );

  const closeCurrentConnection = useCallback(() => {
    eventSourceRef.current?.close();
    eventSourceRef.current = null;

    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
  }, []);

  const connect = useCallback(() => {
    if (!isMountedRef.current) {
      return;
    }

    eventSourceRef.current?.close();

    const cursor = cursorRef.current;

    const eventSource = new EventSource(
      `${NOTIFICATION_API_URL}/api/notifications/events?cursor=${cursor}`,
    );

    eventSourceRef.current = eventSource;

    if (reconnectAttemptRef.current > 0) {
      setConnectionState("reconnecting");
    }

    eventSource.onopen = () => {
      if (!isMountedRef.current) {
        return;
      }

      reconnectAttemptRef.current = 0;
      setConnectionState("connected");
      setError(null);
    };

    eventSource.addEventListener(
      "price_alert_triggered",
      handleNotificationEvent as EventListener,
    );

    eventSource.onerror = () => {
      eventSource.close();

      if (!isMountedRef.current) {
        return;
      }

      reconnectAttemptRef.current += 1;

      if (reconnectAttemptRef.current > MAX_RECONNECT_ATTEMPTS) {
        setConnectionState("disconnected");
        setError("Realtime notifications are disconnected.");
        return;
      }

      setConnectionState("reconnecting");

      const delay = Math.min(
        INITIAL_RECONNECT_DELAY_MS * 2 ** (reconnectAttemptRef.current - 1),
        MAX_RECONNECT_DELAY_MS,
      );

      reconnectTimerRef.current = setTimeout(connect, delay);
    };
  }, [handleNotificationEvent]);

  const retry = useCallback(() => {
    closeCurrentConnection();

    reconnectAttemptRef.current = 0;
    setConnectionState("reconnecting");
    setError(null);

    connect();
  }, [closeCurrentConnection, connect]);

  const resetCursorAndReconnect = useCallback(() => {
    closeCurrentConnection();

    saveCursor(0);
    reconnectAttemptRef.current = 0;
    setConnectionState("reconnecting");
    setError(null);

    connect();
  }, [closeCurrentConnection, connect, saveCursor]);

  useEffect(() => {
    isMountedRef.current = true;
    cursorRef.current = readStoredCursor();

    async function initialize() {
      try {
        setIsLoadingHistory(true);

        const history = await getNotificationHistory(50);

        if (!isMountedRef.current) {
          return;
        }

        setNotifications((current) =>
          mergeNotifications(current, history.events),
        );
      } catch (requestError) {
        if (!isMountedRef.current) {
          return;
        }

        setError(
          requestError instanceof Error
            ? requestError.message
            : "Unable to load notification history",
        );
      } finally {
        if (isMountedRef.current) {
          setIsLoadingHistory(false);
          connect();
        }
      }
    }

    void initialize();

    return () => {
      isMountedRef.current = false;
      closeCurrentConnection();
    };
  }, [connect, closeCurrentConnection]);

  return {
    notifications,
    latestLiveNotification,
    connectionState,
    isLoadingHistory,
    error,
    cursor: cursorRef.current,
    retry,
    resetCursorAndReconnect,
  };
}
