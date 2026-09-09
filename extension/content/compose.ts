/**
 * Gmail Compose Toolbar UI and Event Listeners.
 * (PRD Section 16)
 */

import { queryWithFallback } from "./selectors";
import { handleInterceptedSend } from "./injector";
import { getSettings, saveSettings } from "../shared/storage";

const INITIALIZED_ATTR = "data-pm-compose-init";

/**
 * Injects Mailtrack toggle controls into a newly opened Gmail compose dialog.
 */
export async function setupComposeDialog(composeEl: HTMLElement): Promise<void> {
  if (composeEl.getAttribute(INITIALIZED_ATTR) === "true") {
    return;
  }
  composeEl.setAttribute(INITIALIZED_ATTR, "true");

  const sendButton = queryWithFallback<HTMLElement>(composeEl, "sendButton");
  const toolbar = queryWithFallback<HTMLElement>(composeEl, "composeToolbar");

  if (!sendButton || !toolbar) {
    return;
  }

  // 1. Setup Send Button Click Listener (Capture phase)
  sendButton.addEventListener(
    "click",
    (e) => {
      handleInterceptedSend(composeEl, sendButton, e);
    },
    true
  );

  // 2. Setup Keyboard Shortcuts (Ctrl+Enter / Cmd+Enter)
  composeEl.addEventListener(
    "keydown",
    (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        handleInterceptedSend(composeEl, sendButton, e);
      }
    },
    true
  );

  // 3. Inject Tracking Toggle Button beside Send
  // Check if toolbar already has our controls
  if (toolbar.querySelector(".pm-compose-controls")) {
    return;
  }

  const settings = await getSettings();

  const container = document.createElement("div");
  container.className = "pm-compose-controls";
  container.style.display = "inline-flex";
  container.style.alignItems = "center";
  container.style.marginLeft = "8px";
  container.style.marginRight = "8px";
  container.style.fontFamily = "Google Sans, Roboto, sans-serif";
  container.style.fontSize = "12px";

  // Toggle button
  const toggleBtn = document.createElement("button");
  toggleBtn.type = "button";
  toggleBtn.title = "Personal Mailtrack: Click to Toggle Tracking";
  toggleBtn.style.background = "none";
  toggleBtn.style.border = "1px solid #dadce0";
  toggleBtn.style.borderRadius = "4px";
  toggleBtn.style.padding = "4px 10px";
  toggleBtn.style.cursor = "pointer";
  toggleBtn.style.display = "inline-flex";
  toggleBtn.style.alignItems = "center";
  toggleBtn.style.gap = "4px";
  toggleBtn.style.fontWeight = "500";
  toggleBtn.style.transition = "all 0.15s ease";

  const updateToggleUI = (enabled: boolean) => {
    toggleBtn.innerHTML = enabled
      ? `<span style="color: #0b8043; font-weight: 600;">✓ Tracked</span>`
      : `<span style="color: #5f6368;">✗ Untracked</span>`;
    toggleBtn.style.borderColor = enabled ? "#34a853" : "#dadce0";
    toggleBtn.style.backgroundColor = enabled ? "#e6f4ea" : "#f1f3f4";
  };

  updateToggleUI(settings.trackingEnabled);

  toggleBtn.addEventListener("click", async (e) => {
    e.preventDefault();
    e.stopPropagation();
    const current = await getSettings();
    const newStatus = !current.trackingEnabled;
    await saveSettings({ trackingEnabled: newStatus });
    updateToggleUI(newStatus);
  });

  container.appendChild(toggleBtn);

  // Insert into toolbar
  toolbar.appendChild(container);
}

