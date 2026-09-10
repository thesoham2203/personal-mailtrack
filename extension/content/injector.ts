/**
 * Send interception, pixel injection, link rewriting, and fail-open engine.
 * (PRD Section 17, 18 & Requirement 12, 17)
 */

import { queryWithFallback } from "./selectors";
import { getSettings } from "../shared/storage";
import { proxyFetch } from "../shared/api-proxy";
import { EmailRegisterPayload, EmailRegisterResponse, RecipientInfo } from "../shared/types";

// Double-send prevention map keyed by compose element
const activeSends = new WeakSet<Element>();

/**
 * Extracts recipients, subject, body, and links from a Gmail compose dialog.
 */
export function extractComposeData(composeEl: HTMLElement): {
  recipients: RecipientInfo[];
  subject: string;
  links: string[];
  bodyEl: HTMLElement | null;
} {
  const subjectInput = queryWithFallback<HTMLInputElement>(composeEl, "subjectInput");
  const bodyEl = queryWithFallback<HTMLElement>(composeEl, "messageBody");

  const subject = subjectInput ? subjectInput.value.trim() : "";

  // Extract recipient emails
  const recipients: RecipientInfo[] = [];
  const recipientEls = composeEl.querySelectorAll('span[email], [data-hovercard-id*="@"], input[aria-label*="To"]');
  recipientEls.forEach((el) => {
    const email = el.getAttribute("email") || el.getAttribute("data-hovercard-id") || (el as HTMLInputElement).value;
    if (email && email.includes("@") && !recipients.some((r) => r.email.toLowerCase() === email.toLowerCase())) {
      recipients.push({
        email: email.trim().toLowerCase(),
        name: el.textContent?.trim() || undefined,
        recipient_type: "to",
      });
    }
  });

  // Extract links from HTML body
  const links: string[] = [];
  if (bodyEl) {
    const anchorEls = bodyEl.querySelectorAll("a[href]");
    anchorEls.forEach((a) => {
      const href = a.getAttribute("href");
      if (href && (href.startsWith("http://") || href.startsWith("https://")) && !links.includes(href)) {
        links.push(href);
      }
    });
  }

  return { recipients, subject, links, bodyEl };
}

/**
 * Executes original native Gmail Send action, bypassing tracking interception.
 */
export function triggerNativeSend(sendButton: HTMLElement, composeEl: HTMLElement): void {
  try {
    activeSends.add(composeEl);
    sendButton.dispatchEvent(
      new MouseEvent("click", {
        bubbles: true,
        cancelable: true,
        view: window,
      })
    );
  } finally {
    setTimeout(() => activeSends.delete(composeEl), 2000);
  }
}

/**
 * Intercepts Send action, prepares tracking with fail-open safety, and triggers send.
 */
export async function handleInterceptedSend(
  composeEl: HTMLElement,
  sendButton: HTMLElement,
  event?: Event
): Promise<void> {
  // 1. Double-send check: if already in progress or marked, ignore
  if (activeSends.has(composeEl)) {
    return;
  }

  const settings = await getSettings();

  // If tracking is turned OFF by user, allow native send immediately
  if (!settings.trackingEnabled) {
    return; // Native event proceeds normally
  }

  // Prevent default to intercept send
  if (event) {
    event.preventDefault();
    event.stopImmediatePropagation();
  }

  const { recipients, subject, links, bodyEl } = extractComposeData(composeEl);

  // If no valid recipients found or no body, fail-open to native send
  if (recipients.length === 0 || !bodyEl) {
    console.warn("[Personal Mailtrack] No recipients or body found, sending natively.");
    triggerNativeSend(sendButton, composeEl);
    return;
  }

  const payload: EmailRegisterPayload = {
    subject,
    recipients,
    links: settings.linkTrackingEnabled ? links : [],
  };

  // 2. Prepare tracking with fail-open timeout
  const timeoutMs = settings.prepareTimeoutMs || 2500;
  const timeoutPromise = new Promise<never>((_, reject) =>
    setTimeout(() => reject(new Error("TRACKING_PREPARE_TIMEOUT")), timeoutMs)
  );

  try {
    const responsePromise = proxyFetch(`${settings.apiBaseUrl}/api/v1/emails`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }).then((res) => {
      if (!res.ok) throw new Error(`Backend error status ${res.status}`);
      return res.json() as EmailRegisterResponse;
    });

    const regData = await Promise.race([responsePromise, timeoutPromise]);

    // 3. Success: Inject 1x1 tracking pixel
    if (regData.pixel_url) {
      const pixelImg = document.createElement("img");
      pixelImg.src = regData.pixel_url;
      pixelImg.alt = "";
      pixelImg.width = 1;
      pixelImg.height = 1;
      pixelImg.style.display = "none";
      pixelImg.setAttribute("data-pm-pixel", "true");
      bodyEl.appendChild(pixelImg);
    }

    // 4. Success: Rewrite links with signed redirect URLs
    if (settings.linkTrackingEnabled && regData.links && regData.links.length > 0) {
      const linkMap = new Map(regData.links.map((l) => [l.original_url, l.tracked_url]));
      const anchorEls = bodyEl.querySelectorAll("a[href]");
      anchorEls.forEach((a) => {
        const orig = a.getAttribute("href");
        if (orig && linkMap.has(orig)) {
          a.setAttribute("href", linkMap.get(orig)!);
        }
      });
    }

    console.log("[Personal Mailtrack] Tracking injected successfully:", regData.tracked_email_id);
  } catch (err) {
    // FAIL-OPEN: Under any error (network failure, timeout, 500 error), send natively!
    console.warn("[Personal Mailtrack] Tracking prepare failed open, sending email normally:", err);
  } finally {
    // Dispatch native send to ensure email is sent!
    triggerNativeSend(sendButton, composeEl);
  }
}
