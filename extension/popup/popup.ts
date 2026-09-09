/**
 * Extension popup logic.
 */

import { getSettings, saveSettings } from "../shared/storage";
import { ActivityEventSummary } from "../shared/types";

async function initPopup(): Promise<void> {
  const settings = await getSettings();

  const trackingToggle = document.getElementById("tracking-toggle") as HTMLInputElement;
  const linkToggle = document.getElementById("link-tracking-toggle") as HTMLInputElement;
  const notifToggle = document.getElementById("notifications-toggle") as HTMLInputElement;
  const statusPill = document.getElementById("backend-status") as HTMLElement;
  const activityFeed = document.getElementById("activity-feed") as HTMLElement;

  trackingToggle.checked = settings.trackingEnabled;
  linkToggle.checked = settings.linkTrackingEnabled;
  notifToggle.checked = settings.desktopNotifications;

  trackingToggle.addEventListener("change", () => {
    saveSettings({ trackingEnabled: trackingToggle.checked });
  });

  linkToggle.addEventListener("change", () => {
    saveSettings({ linkTrackingEnabled: linkToggle.checked });
  });

  notifToggle.addEventListener("change", () => {
    saveSettings({ desktopNotifications: notifToggle.checked });
  });

  // Check backend health
  try {
    const res = await fetch(`${settings.apiBaseUrl}/health`);
    if (res.ok) {
      statusPill.textContent = "Online";
      statusPill.className = "status-pill online";
    } else {
      statusPill.textContent = "Error";
      statusPill.className = "status-pill offline";
    }
  } catch (err) {
    statusPill.textContent = "Offline";
    statusPill.className = "status-pill offline";
  }

  // Load recent activity from backend
  try {
    const res = await fetch(`${settings.apiBaseUrl}/api/v1/analytics/activity?limit=5`);
    if (res.ok) {
      const activities: ActivityEventSummary[] = await res.json();
      if (activities.length === 0) {
        activityFeed.innerHTML = `<div style="color: #70757a; text-align: center; padding: 12px;">No activity yet.</div>`;
      } else {
        activityFeed.innerHTML = activities
          .map((a) => {
            const timeStr = new Date(a.occurred_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
            const subject = a.metadata?.subject || "Email";
            const recip = a.metadata?.recipient_email || "";
            const isClick = a.event_type === "email.clicked";
            const icon = isClick ? "↗" : "✓✓";
            return `
              <div class="activity-item">
                <span style="font-weight: bold; color: #1a73e8;">${icon}</span>
                <span>${isClick ? "Clicked" : "Opened"}: <b>${subject}</b></span>
                <div class="activity-time">${recip} · ${timeStr}</div>
              </div>
            `;
          })
          .join("");
      }
    }
  } catch (err) {
    activityFeed.innerHTML = `<div style="color: #d93025;">Could not connect to backend.</div>`;
  }

  // Action links
  document.getElementById("open-dashboard-btn")?.addEventListener("click", (e) => {
    e.preventDefault();
    chrome.tabs.create({ url: "http://localhost:5173" });
  });

  document.getElementById("open-options-btn")?.addEventListener("click", (e) => {
    e.preventDefault();
    chrome.runtime.openOptionsPage();
  });
}

document.addEventListener("DOMContentLoaded", initPopup);
