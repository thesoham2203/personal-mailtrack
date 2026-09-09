/**
 * Desktop notification dispatch module.
 * Wraps chrome.notifications with deduplication and per-type message mapping.
 */

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface NotificationPayload {
  eventType:
    | "email.opened"
    | "email.clicked"
    | "email.replied"
    | "document.viewed"
    | "hot_conversation"
    | "revival";
  subject?: string;
  recipientEmail?: string;
  message?: string;
}

// ---------------------------------------------------------------------------
// In-memory deduplication set
// Tracks notification IDs shown during this service-worker lifetime to avoid
// re-notifying the same event when the alarm fires repeatedly.
// ---------------------------------------------------------------------------

const shownNotificationIds = new Set<string>();

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Build a stable deduplication ID from the payload so that identical events
 * (same type + subject + recipient) are only shown once per worker lifetime.
 */
function buildDedupeId(payload: NotificationPayload): string {
  return `${payload.eventType}|${payload.subject ?? ""}|${payload.recipientEmail ?? ""}`;
}

/**
 * Map an event type to a human-readable title and message string.
 */
function buildTitleAndMessage(payload: NotificationPayload): { title: string; message: string } {
  const subject = payload.subject ? `"${payload.subject}"` : "your email";
  const recipient = payload.recipientEmail || "Someone";

  switch (payload.eventType) {
    case "email.opened":
      return {
        title: "📬 Email Opened!",
        message: payload.message ?? `${recipient} just opened ${subject}`,
      };
    case "email.clicked":
      return {
        title: "🔗 Link Clicked!",
        message: payload.message ?? `A link was clicked in ${subject}`,
      };
    case "email.replied":
      return {
        title: "↩️ Reply Received!",
        message: payload.message ?? `${recipient} replied to ${subject}`,
      };
    case "document.viewed":
      return {
        title: "📄 Document Viewed!",
        message: payload.message ?? `${recipient} viewed a document from ${subject}`,
      };
    case "hot_conversation":
      return {
        title: "🔥 Hot Conversation",
        message: payload.message ?? `${subject} has high engagement — follow up now`,
      };
    case "revival":
      return {
        title: "💡 Revival Opportunity",
        message: payload.message ?? `${recipient} re-engaged with ${subject}`,
      };
    default:
      return {
        title: "Personal Mailtrack",
        message: payload.message ?? "New activity detected",
      };
  }
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Show a Chrome desktop notification for the given payload.
 *
 * Respects the `notificationsEnabled` user preference and deduplicates
 * identical events within the current service-worker lifetime.
 */
export async function showNotification(payload: NotificationPayload): Promise<void> {
  // Check user preference (default: enabled).
  const enabled: boolean = await new Promise((resolve) => {
    chrome.storage.local.get(["notificationsEnabled"], (result) => {
      resolve(result["notificationsEnabled"] !== false);
    });
  });

  if (!enabled) {
    console.log("[notifications] Desktop notifications are disabled — skipping.");
    return;
  }

  // Deduplication check.
  const dedupeId = buildDedupeId(payload);
  if (shownNotificationIds.has(dedupeId)) {
    console.log(`[notifications] Duplicate suppressed: ${dedupeId}`);
    return;
  }
  shownNotificationIds.add(dedupeId);

  const { title, message } = buildTitleAndMessage(payload);

  chrome.notifications.create({
    type: "basic",
    iconUrl: "../icons/icon48.png",
    title,
    message,
    priority: 2,
  });

  console.log(`[notifications] Shown: "${title}" — ${message}`);
}

/**
 * Returns true if the `notifications` permission has been granted.
 * Useful for options-page permission prompts.
 */
export async function checkNotificationsPermission(): Promise<boolean> {
  return new Promise((resolve) => {
    chrome.permissions.contains({ permissions: ["notifications"] }, resolve);
  });
}
