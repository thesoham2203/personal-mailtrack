/**
 * Background Service Worker for Manifest V3 extension.
 * (PRD Section 15, 20 & Requirement 11)
 */

import { getSettings } from "../shared/storage";
import { ActivityEventSummary } from "../shared/types";

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

// Periodic check every 30 seconds
chrome.alarms.create("pm_reconcile_alarm", { periodInMinutes: 0.5 });
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === "pm_reconcile_alarm") {
    reconcileActivityEvents();
  }
});

chrome.runtime.onInstalled.addListener(() => {
  console.log("[Personal Mailtrack] Service worker installed.");
});
