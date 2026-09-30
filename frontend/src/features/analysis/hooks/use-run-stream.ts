"use client";

import { useEffect, useRef, useState } from "react";
import type { ConnectionState } from "../types";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const MAX_RECONNECT_ATTEMPTS = 5;
const INITIAL_RECONNECT_DELAY = 500;
const MAX_RECONNECT_DELAY = 5000;

type RunEventType =
  | "text_delta"
  | "run_completed"
  | "run_failed"
  | "run_interrupted";

interface RunEvent {
  id: string;
  run_id: string;
  sequence: number;
  type: RunEventType;
  payload: {
    text?: string;
    message?: string;
    recoverable?: boolean;
  };
  created_at: string;
}

interface StreamError {
  code: string;
  message: string;
  recoverable: boolean;
}

export function useRunStream() {
  const [connectionState, setConnectionState] =
    useState<ConnectionState>("idle");
  const [responseText, setResponseText] = useState("");
  const [events, setEvents] = useState<RunEvent[]>([]);
  const [cursor, setCursor] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimerRef = useRef<ReturnType<
    typeof setTimeout
  > | null>(null);

  const runIdRef = useRef<string | null>(null);
  const cursorRef = useRef(0);
  const reconnectAttemptsRef = useRef(0);
  const shouldReconnectRef = useRef(false);
  const terminalRef = useRef(false);
  const seenSequencesRef = useRef<Set<number>>(new Set());

  function clearReconnectTimer() {
    if (reconnectTimerRef.current !== null) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
  }

  function closeEventSource() {
    eventSourceRef.current?.close();
    eventSourceRef.current = null;
  }

  function processEvent(event: Event) {
    const messageEvent = event as MessageEvent<string>;
    const runEvent = JSON.parse(messageEvent.data) as RunEvent;
    const sequence = runEvent.sequence;

    // Ignore replay/live overlap and repeated delivery.
    if (
      sequence <= cursorRef.current ||
      seenSequencesRef.current.has(sequence)
    ) {
      return;
    }

    // Never silently accept a gap.
    if (sequence !== cursorRef.current + 1) {
      setError(
        `Event gap detected. Expected ${
          cursorRef.current + 1
        }, received ${sequence}.`,
      );

      closeEventSource();
      scheduleReconnect();
      return;
    }

    seenSequencesRef.current.add(sequence);
    cursorRef.current = sequence;

    setCursor(sequence);
    setEvents((currentEvents) => [
      ...currentEvents,
      runEvent,
    ]);

    if (
      runEvent.type === "text_delta" &&
      runEvent.payload.text
    ) {
      setResponseText(
        (currentText) =>
          currentText + runEvent.payload.text,
      );
    }

    if (runEvent.type === "run_completed") {
      terminalRef.current = true;
      shouldReconnectRef.current = false;
      setConnectionState("completed");
      closeEventSource();
    }

    if (runEvent.type === "run_failed") {
      terminalRef.current = true;
      shouldReconnectRef.current = false;
      setError(
        runEvent.payload.message ??
          "Stock analysis generation failed.",
      );
      setConnectionState("failed");
      closeEventSource();
    }

    if (runEvent.type === "run_interrupted") {
      terminalRef.current = true;
      shouldReconnectRef.current = false;
      setError(
        runEvent.payload.message ??
          "Generation was interrupted.",
      );
      setConnectionState("interrupted");
      closeEventSource();
    }
  }

  function openStream(
    runId: string,
    streamCursor: number,
    attempt: number,
  ) {
    clearReconnectTimer();
    closeEventSource();

    if (!shouldReconnectRef.current) {
      return;
    }

    if (attempt === 0 && streamCursor === 0) {
      setConnectionState("connecting");
    } else {
      setConnectionState("reconnecting");
    }

    const streamUrl =
      `${API_URL}/api/runs/${runId}/events` +
      `?cursor=${streamCursor}`;

    const eventSource = new EventSource(streamUrl);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      reconnectAttemptsRef.current = 0;
      setError(null);
      setConnectionState("connected");
    };

    eventSource.addEventListener(
      "text_delta",
      processEvent,
    );
    eventSource.addEventListener(
      "run_completed",
      processEvent,
    );
    eventSource.addEventListener(
      "run_failed",
      processEvent,
    );
    eventSource.addEventListener(
      "run_interrupted",
      processEvent,
    );

    eventSource.addEventListener(
      "stream_error",
      (event: Event) => {
        const messageEvent =
          event as MessageEvent<string>;

        const streamError = JSON.parse(
          messageEvent.data,
        ) as StreamError;

        setError(streamError.message);
        closeEventSource();

        if (streamError.recoverable) {
          scheduleReconnect();
        } else {
          shouldReconnectRef.current = false;
          setConnectionState("failed");
        }
      },
    );

    eventSource.onerror = () => {
      closeEventSource();

      if (
        terminalRef.current ||
        !shouldReconnectRef.current
      ) {
        return;
      }

      scheduleReconnect();
    };
  }

  function scheduleReconnect() {
    const runId = runIdRef.current;

    if (
      !runId ||
      terminalRef.current ||
      !shouldReconnectRef.current
    ) {
      return;
    }

    const attempt = reconnectAttemptsRef.current;

    if (attempt >= MAX_RECONNECT_ATTEMPTS) {
      shouldReconnectRef.current = false;
      setConnectionState("disconnected");
      setError(
        `Unable to reconnect after ${MAX_RECONNECT_ATTEMPTS} attempts.`,
      );
      return;
    }

    const delay = Math.min(
      INITIAL_RECONNECT_DELAY * 2 ** attempt,
      MAX_RECONNECT_DELAY,
    );

    reconnectAttemptsRef.current += 1;
    setConnectionState("reconnecting");

    reconnectTimerRef.current = setTimeout(() => {
      openStream(
        runId,
        cursorRef.current,
        reconnectAttemptsRef.current,
      );
    }, delay);
  }

  function startStream(runId: string) {
    clearReconnectTimer();
    closeEventSource();

    runIdRef.current = runId;
    cursorRef.current = 0;
    reconnectAttemptsRef.current = 0;
    shouldReconnectRef.current = true;
    terminalRef.current = false;
    seenSequencesRef.current = new Set();

    setResponseText("");
    setEvents([]);
    setCursor(0);
    setError(null);
    setConnectionState("connecting");

    openStream(runId, 0, 0);
  }

  function disconnect() {
    shouldReconnectRef.current = false;

    clearReconnectTimer();
    closeEventSource();

    if (!terminalRef.current) {
      setConnectionState("disconnected");
    }
  }

  function reconnect() {
    const runId = runIdRef.current;

    if (!runId || terminalRef.current) {
      return;
    }

    shouldReconnectRef.current = true;
    reconnectAttemptsRef.current = 0;
    setError(null);

    openStream(runId, cursorRef.current, 1);
  }

  useEffect(() => {
    return () => {
      shouldReconnectRef.current = false;
      clearReconnectTimer();
      closeEventSource();
    };
  }, []);

  return {
    connectionState,
    responseText,
    events,
    cursor,
    error,
    startStream,
    disconnect,
    reconnect,
  };
}