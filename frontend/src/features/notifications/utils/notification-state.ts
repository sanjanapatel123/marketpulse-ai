import type {
  NotificationEvent,
} from "../types/notification";


export function mergeNotifications(
  current: NotificationEvent[],
  incoming: NotificationEvent[],
  maximumEvents = 100,
): NotificationEvent[] {
  const eventsBySequence = new Map<
    number,
    NotificationEvent
  >();

  for (const event of current) {
    eventsBySequence.set(
      event.sequence,
      event,
    );
  }

  for (const event of incoming) {
    eventsBySequence.set(
      event.sequence,
      event,
    );
  }

  return Array.from(
    eventsBySequence.values(),
  )
    .sort(
      (first, second) =>
        second.sequence - first.sequence,
    )
    .slice(0, maximumEvents);
}


export function shouldAcceptNotification(
  notification: NotificationEvent,
  currentCursor: number,
): boolean {
  return (
    Number.isInteger(notification.sequence) &&
    notification.sequence > currentCursor
  );
}


export function parseStoredCursor(
  storedValue: string | null,
): number {
  if (!storedValue) {
    return 0;
  }

  const parsed = Number(storedValue);

  if (
    !Number.isInteger(parsed) ||
    parsed < 0
  ) {
    return 0;
  }

  return parsed;
}