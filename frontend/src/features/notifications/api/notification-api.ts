import type { NotificationHistoryResponse } from "../types/notification";

export const NOTIFICATION_API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function getNotificationHistory(
  limit = 50,
): Promise<NotificationHistoryResponse> {
  const response = await fetch(
    `${NOTIFICATION_API_URL}/api/notifications?limit=${limit}`,
    {
      cache: "no-store",
    },
  );

  if (!response.ok) {
    let message = "Unable to load notifications";

    try {
      const body = await response.json();
      message = body.detail?.message ?? message;
    } catch {
      // Keep fallback message.
    }

    throw new Error(message);
  }

  return response.json();
}
