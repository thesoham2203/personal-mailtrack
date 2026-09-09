/**
 * Typed API client for communication with the Personal Mailtrack FastAPI backend.
 * Reads apiBaseUrl and apiKey from chrome.storage.local on every call so that
 * options-page changes are picked up immediately without reloading the worker.
 */

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface ActivityEvent {
  id: string;
  event_type: string;
  occurred_at: string;
  entity_type: string;
  metadata: Record<string, unknown>;
}

export interface EmailStatus {
  id: string;
  subject: string;
  human_open_count: number;
  click_count: number;
  replied_at: string | null;
}

export interface FollowUpSummary {
  hot: number;
  revival: number;
  waiting_on_them: number;
  no_reply: number;
}

export interface SyncResult {
  status: string;
  synced?: number;
}

// ---------------------------------------------------------------------------
// Storage helpers
// ---------------------------------------------------------------------------

async function getStorageValues(): Promise<{ apiBaseUrl: string; apiKey: string }> {
  return new Promise((resolve) => {
    chrome.storage.local.get(["apiBaseUrl", "apiKey"], (result) => {
      resolve({
        apiBaseUrl: (result["apiBaseUrl"] as string) || "http://localhost:8000",
        apiKey: (result["apiKey"] as string) || "",
      });
    });
  });
}

// ---------------------------------------------------------------------------
// Core fetch helper
// ---------------------------------------------------------------------------

/**
 * Generic fetch wrapper. Returns the parsed JSON response, or null on any
 * network / HTTP error. All errors are logged to the console.
 */
export async function fetchApi(path: string, options: RequestInit = {}): Promise<unknown> {
  const { apiBaseUrl, apiKey } = await getStorageValues();

  const url = `${apiBaseUrl}${path}`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (apiKey) {
    headers["X-API-Key"] = apiKey;
  }

  try {
    const res = await fetch(url, { ...options, headers });
    if (!res.ok) {
      console.warn(`[api-client] HTTP ${res.status} for ${url}`);
      return null;
    }
    return (await res.json()) as unknown;
  } catch (err) {
    console.error(`[api-client] Network error for ${url}:`, err);
    return null;
  }
}

// ---------------------------------------------------------------------------
// Typed API functions
// ---------------------------------------------------------------------------

/**
 * Fetch recent activity events from the backend.
 * @param limit Maximum number of events to retrieve (default: 20).
 */
export async function getActivityFeed(limit = 20): Promise<ActivityEvent[]> {
  const data = await fetchApi(`/api/v1/analytics/activity?limit=${limit}`);
  return Array.isArray(data) ? (data as ActivityEvent[]) : [];
}

/**
 * Fetch status for a single tracked email by its backend ID.
 */
export async function getEmailStatus(emailId: string): Promise<EmailStatus | null> {
  const data = await fetchApi(`/api/v1/emails/${encodeURIComponent(emailId)}/status`);
  return data ? (data as EmailStatus) : null;
}

/**
 * Fetch the follow-up category summary (hot / revival / waiting / no-reply counts).
 */
export async function getFollowUpSummary(): Promise<FollowUpSummary | null> {
  const data = await fetchApi("/api/v1/analytics/follow-up-summary");
  return data ? (data as FollowUpSummary) : null;
}

/**
 * Trigger a backend reconciliation sync and return the result.
 */
export async function triggerSync(): Promise<SyncResult | null> {
  const data = await fetchApi("/api/v1/sync/trigger", { method: "POST" });
  return data ? (data as SyncResult) : null;
}

/**
 * Ping the backend health endpoint. Returns true if the backend is reachable
 * and responding with a 2xx status.
 */
export async function healthCheck(): Promise<boolean> {
  const data = await fetchApi("/health");
  return data !== null;
}
