/**
 * Shared constants and default configurations.
 */

import { TrackingSettings } from "./types";

export const DEFAULT_SETTINGS: TrackingSettings = {
  apiBaseUrl: "http://localhost:8000",
  trackingBaseUrl: "http://localhost:8000",
  trackingEnabled: true,
  linkTrackingEnabled: true,
  prepareTimeoutMs: 2500, // PRD Req 12: Configurable 2000-3000ms fail-open timeout
  desktopNotifications: true,
};

export const STORAGE_KEYS = {
  SETTINGS: "pm_settings",
  DIAGNOSTICS: "pm_diagnostics",
  RECENT_ACTIVITY: "pm_recent_activity",
};
