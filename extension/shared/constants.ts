/**
 * Shared constants and default configurations.
 */

import { TrackingSettings } from "./types";

export const DEFAULT_SETTINGS: TrackingSettings = {
  apiBaseUrl: "https://personal-mailtrack-api.onrender.com",
  trackingBaseUrl: "https://personal-mailtrack-api.onrender.com",
  trackingEnabled: true,
  linkTrackingEnabled: true,
  prepareTimeoutMs: 3000, // PRD Req 12: Configurable fail-open timeout
  desktopNotifications: true,
};

export const STORAGE_KEYS = {
  SETTINGS: "pm_settings",
  DIAGNOSTICS: "pm_diagnostics",
  RECENT_ACTIVITY: "pm_recent_activity",
};
