/**
 * Options page logic.
 */

import { getSettings, saveSettings } from "../shared/storage";

async function initOptions(): Promise<void> {
  const settings = await getSettings();

  const apiInput = document.getElementById("api-url") as HTMLInputElement;
  const trackingInput = document.getElementById("tracking-url") as HTMLInputElement;
  const timeoutInput = document.getElementById("timeout-ms") as HTMLInputElement;
  const form = document.getElementById("settings-form") as HTMLFormElement;
  const alertEl = document.getElementById("save-alert") as HTMLElement;

  apiInput.value = settings.apiBaseUrl;
  trackingInput.value = settings.trackingBaseUrl;
  timeoutInput.value = String(settings.prepareTimeoutMs);

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    await saveSettings({
      apiBaseUrl: apiInput.value.trim().replace(/\/+$/, ""),
      trackingBaseUrl: trackingInput.value.trim().replace(/\/+$/, ""),
      prepareTimeoutMs: parseInt(timeoutInput.value, 10) || 2500,
    });

    alertEl.style.display = "block";
    setTimeout(() => {
      alertEl.style.display = "none";
    }, 3000);
  });
}

document.addEventListener("DOMContentLoaded", initOptions);
