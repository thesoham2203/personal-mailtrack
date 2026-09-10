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
  // 1. Direct fetch (fastest, independent of service worker lifecycle)
  // Backend CORS explicitly allows https://mail.google.com
  try {
    const directRes = await fetch(url, {
      method: options.method || "GET",
      headers: options.headers || {},
      body: options.body,
    });
    const textBody = await directRes.text();
    return {
      ok: directRes.ok,
      status: directRes.status,
      text: () => textBody,
      json: () => JSON.parse(textBody),
    };
  } catch (directErr) {
    // 2. Service worker proxy fallback (if direct fetch blocked or network error)
    if (typeof chrome !== "undefined" && chrome?.runtime?.sendMessage && chrome?.runtime?.id) {
      try {
        const result = await new Promise<ProxyResponse>((resolve, reject) => {
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
              resolve(response);
            }
          );
        });

        if (result.error && result.status === 0) {
          throw new Error(result.error);
        }

        return {
          ok: result.ok,
          status: result.status,
          text: () => result.body,
          json: () => JSON.parse(result.body),
        };
      } catch {
        // Fall through to throw original direct fetch error
      }
    }

    throw directErr;
  }
}


