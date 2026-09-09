/**
 * Main Content Script for Gmail Web.
 */

import { setupComposeDialog } from "./compose";
import { decorateMessageRows } from "./sent";
import { showDebuggerModal } from "./debugger";
import { queryWithFallback } from "./selectors";

console.log("[Personal Mailtrack] Extension loaded into Gmail Web.");

// Hotkey listener for Mailtrack Debugger (Ctrl+Shift+D)
window.addEventListener("keydown", (e) => {
  if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === "d") {
    e.preventDefault();
    showDebuggerModal();
  }
});

/**
 * Scan DOM for active compose dialogs and un-decorated sent message rows.
 */
function scanGmailDOM(): void {
  // 1. Detect open compose dialogs
  const composeViews = document.querySelectorAll('div[role="dialog"], div.M9');
  composeViews.forEach((el) => {
    if (el instanceof HTMLElement) {
      // If this is an inner container (.M9) and its parent dialog is already present, skip
      if (el.classList.contains("M9") && el.closest('div[role="dialog"]')) {
        return;
      }
      const sendBtn = queryWithFallback<HTMLElement>(el, "sendButton");
      if (sendBtn) {
        setupComposeDialog(el);
      }
    }
  });

  // 2. Decorate list message rows with checkmarks
  decorateMessageRows();
}

// Observe Gmail single-page app mutations
const observer = new MutationObserver(() => {
  scanGmailDOM();
});

observer.observe(document.body, {
  childList: true,
  subtree: true,
});

// Run initial scan
setTimeout(scanGmailDOM, 1500);
