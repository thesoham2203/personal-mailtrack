/**
 * Auth module — credential storage and connection management.
 *
 * Auth state is stored as flat keys directly in chrome.storage.local so that
 * individual values can be retrieved cheaply without deserialising the full
 * pm_settings blob used by the tracking layer.
 */

import { healthCheck } from "./api-client";

// ---------------------------------------------------------------------------
// Storage keys (const enum kept local — not re-exported to avoid coupling)
// ---------------------------------------------------------------------------

const STORAGE_KEYS = {
  API_BASE_URL: "apiBaseUrl",
  API_KEY: "apiKey",
  IS_LOGGED_IN: "isLoggedIn",
  USER_ID: "userId",
} as const;

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface AuthState {
  isLoggedIn: boolean;
  apiBaseUrl: string;
  apiKey: string;
  userId: string | null;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function storageGet<T extends Record<string, unknown>>(keys: string[]): Promise<T> {
  return new Promise((resolve) => {
    chrome.storage.local.get(keys, (result) => resolve(result as T));
  });
}

function storageSet(items: Record<string, unknown>): Promise<void> {
  return new Promise((resolve) => {
    chrome.storage.local.set(items, resolve);
  });
}

function storageRemove(keys: string[]): Promise<void> {
  return new Promise((resolve) => {
    chrome.storage.local.remove(keys, resolve);
  });
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Return the current authentication state from storage.
 * Never throws — missing values fall back to safe defaults.
 */
export async function getAuthState(): Promise<AuthState> {
  const result = await storageGet<Record<string, unknown>>([
    STORAGE_KEYS.API_BASE_URL,
    STORAGE_KEYS.API_KEY,
    STORAGE_KEYS.IS_LOGGED_IN,
    STORAGE_KEYS.USER_ID,
  ]);

  return {
    isLoggedIn: (result[STORAGE_KEYS.IS_LOGGED_IN] as boolean) === true,
    apiBaseUrl: (result[STORAGE_KEYS.API_BASE_URL] as string) || "https://personal-mailtrack-api.onrender.com",
    apiKey: (result[STORAGE_KEYS.API_KEY] as string) || "",
    userId: (result[STORAGE_KEYS.USER_ID] as string | undefined) ?? null,
  };
}

/**
 * Persist new connection settings after validating them against the backend.
 *
 * The function temporarily writes the supplied values to storage so that the
 * shared `healthCheck()` helper (which reads storage) can use them during
 * validation.  If the health check fails the original values are restored and
 * an error is thrown.
 */
export async function saveConnectionSettings(
  apiBaseUrl: string,
  apiKey: string
): Promise<void> {
  // Snapshot current values so we can roll back on failure.
  const previous = await storageGet<Record<string, unknown>>([
    STORAGE_KEYS.API_BASE_URL,
    STORAGE_KEYS.API_KEY,
  ]);

  // Write candidate values — healthCheck() will read them.
  await storageSet({
    [STORAGE_KEYS.API_BASE_URL]: apiBaseUrl.trim().replace(/\/+$/, ""),
    [STORAGE_KEYS.API_KEY]: apiKey.trim(),
  });

  const ok = await healthCheck();

  if (!ok) {
    // Roll back to previous values.
    await storageSet({
      [STORAGE_KEYS.API_BASE_URL]: previous[STORAGE_KEYS.API_BASE_URL] ?? "https://personal-mailtrack-api.onrender.com",
      [STORAGE_KEYS.API_KEY]: previous[STORAGE_KEYS.API_KEY] ?? "",
    });
    throw new Error(
      `Cannot reach backend at ${apiBaseUrl}. Check the URL and API key then try again.`
    );
  }

  // Persist authenticated state.
  await storageSet({ [STORAGE_KEYS.IS_LOGGED_IN]: true });
  console.log("[auth] Connection settings saved and validated.");
}

/**
 * Clear the authenticated session while keeping the saved base URL so the
 * options page can pre-populate the field on next open.
 */
export async function logout(): Promise<void> {
  await storageRemove([STORAGE_KEYS.API_KEY, STORAGE_KEYS.IS_LOGGED_IN, STORAGE_KEYS.USER_ID]);
  console.log("[auth] Logged out.");
}

/**
 * Return the stored API base URL, defaulting to localhost.
 */
export async function getApiBaseUrl(): Promise<string> {
  const result = await storageGet<Record<string, unknown>>([STORAGE_KEYS.API_BASE_URL]);
  return (result[STORAGE_KEYS.API_BASE_URL] as string) || "https://personal-mailtrack-api.onrender.com";
}

/**
 * Return the stored API key (empty string if not set).
 */
export async function getApiKey(): Promise<string> {
  const result = await storageGet<Record<string, unknown>>([STORAGE_KEYS.API_KEY]);
  return (result[STORAGE_KEYS.API_KEY] as string) || "";
}
