/**
 * API proxy helper for content scripts.
 *
 * Content scripts run inside the Gmail page context and are subject to CORS.
 * This module routes all API calls through the background service worker, which
 * has host_permissions and is completely exempt from CORS restrictions.
 */

export interface ProxyResponse {
  ok: boolean;
  status: number;
  body: string;
  error?: string;
}

/**
 * Sends an API request through the background service worker to bypass CORS.
 * Drop-in replacement for fetch() in content scripts.
 */
export async function proxyFetch(
  url: string,
  options: { method?: string; headers?: Record<string, string>; body?: string } = {}
): Promise<{ ok: boolean; status: number; json: () => unknown; text: () => string }> {
  return new Promise((resolve, reject) => {
    try {
      if (typeof chrome === "undefined" || !chrome?.runtime?.sendMessage) {
        reject(new Error("Extension context unavailable"));
        return;
      }
      chrome.runtime.sendMessage(
        {
          type: "FETCH_API",
          payload: {
            url,
            method: options.method || "GET",
            headers: options.headers || {},
            body: options.body,
          },
        },
        (response: ProxyResponse) => {
          if (chrome.runtime?.lastError) {
            reject(new Error(chrome.runtime.lastError.message));
            return;
          }
          if (!response) {
            reject(new Error("No response from service worker"));
            return;
          }
          if (response.error && response.status === 0) {
            reject(new Error(response.error));
            return;
          }
          resolve({
            ok: response.ok,
            status: response.status,
            text: () => response.body,
            json: () => JSON.parse(response.body),
          });
        }
      );
    } catch (err) {
      reject(err);
    }
  });
}
