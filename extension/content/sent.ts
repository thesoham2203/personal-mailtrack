/**
 * Gmail Sent & Inbox Message List Checkmarks and Status Indicators.
 * (PRD Section 19)
 */

import { queryAllWithFallback } from "./selectors";
import { getSettings } from "../shared/storage";

interface EmailSummary {
  id: string;
  subject?: string;
  open_count: number;
  click_count: number;
  has_replied: boolean;
  is_hot: boolean;
  sent_at: string;
}

let cachedEmails: Map<string, EmailSummary> = new Map();
let lastFetchTime = 0;

/**
 * Fetches recent tracked emails from backend to decorate rows.
 */
async function refreshTrackedEmailsCache(): Promise<void> {
  const now = Date.now();
  if (now - lastFetchTime < 10000 && cachedEmails.size > 0) {
    return; // Cache valid for 10s
  }

  const settings = await getSettings();
  try {
    const res = await fetch(`${settings.apiBaseUrl}/api/v1/emails?limit=100`);
    if (!res.ok) return;
    const list: EmailSummary[] = await res.json();
    cachedEmails.clear();
    for (const item of list) {
      if (item.subject) {
        cachedEmails.set(item.subject.trim().toLowerCase(), item);
      }
    }
    lastFetchTime = now;
  } catch (err) {
    // Fail silent if backend offline
  }
}

/**
 * Decorates message rows in Gmail tables with checkmarks and tooltips.
 */
export async function decorateMessageRows(): Promise<void> {
  await refreshTrackedEmailsCache();
  if (cachedEmails.size === 0) return;

  const rows = queryAllWithFallback<HTMLTableRowElement>(document, "messageRows");
  for (const row of rows) {
    if (row.getAttribute("data-pm-checked") === "true") continue;

    // Extract subject
    const subjectEl = row.querySelector("span.bog, span[data-thread-id]");
    const subjectText = subjectEl?.textContent?.trim().toLowerCase();

    if (subjectText && cachedEmails.has(subjectText)) {
      const email = cachedEmails.get(subjectText)!;
      row.setAttribute("data-pm-checked", "true");

      // Create badge element
      const badge = document.createElement("span");
      badge.className = "pm-status-badge";
      badge.style.display = "inline-flex";
      badge.style.alignItems = "center";
      badge.style.marginRight = "6px";
      badge.style.fontSize = "13px";
      badge.style.fontWeight = "bold";
      badge.style.cursor = "help";

      if (email.is_hot) {
        badge.innerHTML = `<span style="color: #e37400;" title="🔥 Hot Conversation (${email.open_count} opens)">🔥✓✓</span>`;
      } else if (email.has_replied) {
        badge.innerHTML = `<span style="color: #1a73e8;" title="↩ Replied">↩✓✓</span>`;
      } else if (email.click_count > 0) {
        badge.innerHTML = `<span style="color: #1e8e3e;" title="↗ Link Clicked (${email.click_count} clicks)">↗✓✓</span>`;
      } else if (email.open_count > 0) {
        badge.innerHTML = `<span style="color: #1e8e3e;" title="✓✓ Opened (${email.open_count} times)">✓✓</span>`;
      } else {
        badge.innerHTML = `<span style="color: #5f6368;" title="✓ Sent & Tracked (Unopened)">✓</span>`;
      }

      // Insert before subject line
      if (subjectEl && subjectEl.parentElement) {
        subjectEl.parentElement.insertBefore(badge, subjectEl);
      }
    }
  }
}
