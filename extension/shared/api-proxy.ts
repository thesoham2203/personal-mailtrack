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
  // 1. Try proxying through the service worker (bypasses CORS via host_permissions)
  try {
    if (typeof chrome !== "undefined" && chrome?.runtime?.sendMessage && chrome?.runtime?.id) {
      const result = await new Promise<ProxyResponse>((resolve, reject) => {
        try {
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
        } catch (sendErr) {
          reject(sendErr);
        }
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
    }
  } catch (proxyErr) {
    // If service worker is sleeping, extension was reloaded (context invalidated),
    // or sendMessage failed, seamlessly fall back to direct fetch.
    // This succeeds because the backend CORS policy explicitly allows https://mail.google.com.
    console.warn(
      "[Personal Mailtrack] Service worker proxy unavailable, falling back to direct fetch:",
      proxyErr
    );
  }

  // 2. Direct fetch fallback
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
}

