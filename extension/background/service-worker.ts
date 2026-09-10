/**
 * Background Service Worker for Manifest V3 extension.
 * (PRD Section 15, 20 & Requirement 11)
 */

import { getSettings } from "../shared/storage";
import { ActivityEventSummary } from "../shared/types";
import { setupPeriodicSync, handleAlarmFired, syncActivity } from "./sync";
import { showNotification, NotificationPayload } from "./notifications";
import { getAuthState } from "./auth";

let lastCheckedActivityTime = new Date().toISOString();

/**
 * Polls backend reconciliation API for new activity events and triggers Chrome notifications.
 */
async function reconcileActivityEvents(): Promise<void> {
  const settings = await getSettings();
  if (!settings.desktopNotifications) return;

  try {
    const res = await fetch(`${settings.apiBaseUrl}/api/v1/analytics/activity?limit=10`);
    if (!res.ok) return;

    const events: ActivityEventSummary[] = await res.json();
    const newEvents = events.filter((e) => e.occurred_at > lastCheckedActivityTime);

    for (const ev of newEvents) {
      if (ev.event_type === "email.opened") {
        const subject = ev.metadata?.subject || "your email";
        const recip = ev.metadata?.recipient_email || "Recipient";
        chrome.notifications.create({
          type: "basic",
          iconUrl: "icons/icon48.png",
          title: "Email Opened!",
          message: `${recip} just opened "${subject}"`,
          priority: 2,
        });
      } else if (ev.event_type === "email.clicked") {
        const subject = ev.metadata?.subject || "your email";
        chrome.notifications.create({
          type: "basic",
          iconUrl: "icons/icon48.png",
          title: "Link Clicked!",
          message: `A link was clicked in "${subject}"`,
          priority: 2,
        });
      }
    }

    if (events.length > 0) {
      lastCheckedActivityTime = events[0].occurred_at;
    }
  } catch (err) {
    // Fail silent if backend offline
  }
}

// ---------------------------------------------------------------------------
// Alarms
// ---------------------------------------------------------------------------

// Legacy reconciliation alarm (every 30 seconds).
chrome.alarms.create("pm_reconcile_alarm", { periodInMinutes: 0.5 });

// New structured sync alarm (every 1 minute).
setupPeriodicSync();

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === "pm_reconcile_alarm") {
    reconcileActivityEvents();
  }
  // Delegate all other alarms (including 'mailtrack-sync') to sync module.
  handleAlarmFired(alarm.name);
});

// ---------------------------------------------------------------------------
// Lifecycle
// ---------------------------------------------------------------------------

chrome.runtime.onInstalled.addListener(() => {
  console.log("[Personal Mailtrack] Service worker installed.");
  // Re-register the periodic sync alarm on install / update.
  setupPeriodicSync();
});

// ---------------------------------------------------------------------------
// Message passing — handles requests from popup, options page & content scripts
// ---------------------------------------------------------------------------

chrome.runtime.onMessage.addListener(
  (
    message: { type: string; payload?: unknown },
    _sender,
    sendResponse: (response?: unknown) => void
  ) => {
    switch (message.type) {
      case "SHOW_NOTIFICATION": {
        showNotification(message.payload as NotificationPayload)
          .then(() => sendResponse({ ok: true }))
          .catch((err) => sendResponse({ ok: false, error: String(err) }));
        return true; // Keep the message channel open for the async response.
      }

      case "TRIGGER_SYNC": {
        syncActivity()
          .then(() => sendResponse({ ok: true }))
          .catch((err) => sendResponse({ ok: false, error: String(err) }));
        return true;
      }

      case "GET_AUTH_STATE": {
        getAuthState()
          .then((state) => sendResponse(state))
          .catch((err) => sendResponse({ error: String(err) }));
        return true;
      }

      case "FETCH_API": {
        const payload = message.payload as {
          url: string;
          method?: string;
          headers?: Record<string, string>;
          body?: string;
        } | undefined;

        if (!payload?.url) {
          sendResponse({ ok: false, status: 0, error: "Missing payload or URL" });
          return false;
        }

        fetch(payload.url, {
          method: payload.method || "GET",
          headers: payload.headers || {},
          body: payload.method && payload.method !== "GET" && payload.method !== "HEAD" ? payload.body : undefined,
        })
          .then(async (res) => {
            const text = await res.text();
            sendResponse({ ok: res.ok, status: res.status, body: text });
          })
          .catch((err) => {
            sendResponse({ ok: false, status: 0, error: String(err) });
          });
        return true; // async response
      }

      default:
        // Unknown message type — ignore.
        return false;
    }
  }
);
