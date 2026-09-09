/**
 * Periodic sync module — polls the backend and caches results for the popup.
 *
 * In Manifest V3, service workers are ephemeral.  setInterval() is NOT used;
 * instead chrome.alarms provides reliable periodic wake-up.
 */

import { getActivityFeed } from "./api-client";
import { STORAGE_KEYS } from "../shared/constants";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/** Alarm name — must be unique within the extension. */
const ALARM_NAME = "mailtrack-sync";

/** How often the alarm fires (minutes). Must match SYNC_INTERVAL_MS intent. */
const ALARM_PERIOD_MINUTES = 1;

/** Exported for reference / tests — not actually passed to setInterval. */
export const SYNC_INTERVAL_MS = ALARM_PERIOD_MINUTES * 60_000;

// ---------------------------------------------------------------------------
// Core sync logic
// ---------------------------------------------------------------------------

/**
 * Fetch recent activity from the backend and persist it in storage so the
 * popup can read it without making its own API calls.
 */
export async function syncActivity(): Promise<void> {
  console.log("[sync] syncActivity() start");
  try {
    const events = await getActivityFeed(20);

    await new Promise<void>((resolve) => {
      chrome.storage.local.set(
        {
          [STORAGE_KEYS.RECENT_ACTIVITY]: events,
          lastSyncAt: new Date().toISOString(),
        },
        resolve
      );
    });

    console.log(`[sync] Stored ${events.length} activity event(s).`);
  } catch (err) {
    console.error("[sync] syncActivity() failed:", err);
  }
}

// ---------------------------------------------------------------------------
// Alarm management
// ---------------------------------------------------------------------------

/**
 * Register the periodic chrome alarm.  Safe to call on every service-worker
 * startup — `chrome.alarms.create` is a no-op when an alarm with the same
 * name already exists (unless `when` / `delayInMinutes` are omitted and only
 * `periodInMinutes` is provided, in which case Chromium re-arms it).
 *
 * Call this inside `chrome.runtime.onInstalled` and also at the top level of
 * the service worker so the alarm survives worker restarts.
 */
export function setupPeriodicSync(): void {
  chrome.alarms.create(ALARM_NAME, { periodInMinutes: ALARM_PERIOD_MINUTES });
  console.log(`[sync] Periodic sync alarm registered (every ${ALARM_PERIOD_MINUTES} min).`);
}

/**
 * Dispatch function for chrome.alarms.onAlarm — wire this up in the service
 * worker so that alarm events are routed here.
 */
export async function handleAlarmFired(alarmName: string): Promise<void> {
  if (alarmName === ALARM_NAME) {
    await syncActivity();
  }
}
