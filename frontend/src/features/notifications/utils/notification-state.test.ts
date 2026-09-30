import { describe, expect, it } from "vitest";

import type { NotificationEvent } from "../types/notification";

import {
  mergeNotifications,
  parseStoredCursor,
  shouldAcceptNotification,
} from "./notification-state";

function createEvent(sequence: number): NotificationEvent {
  return {
    id: `notification-${sequence}`,
    sequence,
    type: "price_alert_triggered",
    source_id: `alert-${sequence}`,
    source_type: "price_alert",
    payload: {
      alert_id: `alert-${sequence}`,
      watchlist_id: "watchlist-001",
      symbol: "TCS",
      exchange: "NSE",
      currency: "INR",
      condition: "PRICE_BELOW",
      threshold: "4300.00",
      triggered_price: "4215.60",
      title: "TCS price alert triggered",
      message: "TCS moved below ₹4,300.00 at ₹4,215.60.",
    },
    created_at: "2026-09-30T12:00:00.000Z",
  };
}

describe("mergeNotifications", () => {
  it("sorts events by descending sequence", () => {
    const result = mergeNotifications(
      [createEvent(1)],
      [createEvent(3), createEvent(2)],
    );

    expect(result.map((event) => event.sequence)).toEqual([3, 2, 1]);
  });

  it("deduplicates replay and live overlap", () => {
    const replayed = [createEvent(1), createEvent(2), createEvent(3)];

    const overlappingLiveEvents = [
      createEvent(3),
      createEvent(4),
      createEvent(5),
    ];

    const result = mergeNotifications(replayed, overlappingLiveEvents);

    expect(result.map((event) => event.sequence)).toEqual([5, 4, 3, 2, 1]);

    expect(result).toHaveLength(5);
  });

  it("keeps only the configured maximum", () => {
    const events = Array.from(
      {
        length: 10,
      },
      (_, index) => createEvent(index + 1),
    );

    const result = mergeNotifications([], events, 3);

    expect(result.map((event) => event.sequence)).toEqual([10, 9, 8]);
  });
});

describe("shouldAcceptNotification", () => {
  it("accepts an event after the cursor", () => {
    expect(shouldAcceptNotification(createEvent(11), 10)).toBe(true);
  });

  it("rejects a duplicate at the cursor", () => {
    expect(shouldAcceptNotification(createEvent(10), 10)).toBe(false);
  });

  it("rejects an older replayed event", () => {
    expect(shouldAcceptNotification(createEvent(8), 10)).toBe(false);
  });
});

describe("parseStoredCursor", () => {
  it("parses a valid cursor", () => {
    expect(parseStoredCursor("42")).toBe(42);
  });

  it("returns zero for invalid cursor", () => {
    expect(parseStoredCursor("invalid")).toBe(0);
  });

  it("returns zero for negative cursor", () => {
    expect(parseStoredCursor("-10")).toBe(0);
  });

  it("returns zero when no cursor exists", () => {
    expect(parseStoredCursor(null)).toBe(0);
  });
});
