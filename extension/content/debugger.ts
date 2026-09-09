/**
 * Mailtrack In-Browser Debugger and Diagnostics Modal.
 * (PRD Requirement 13 & 35)
 */

import { queryWithFallback, selectorDiagnostics } from "./selectors";
import { getSettings, saveDiagnostics } from "../shared/storage";
import { DiagnosticsReport } from "../shared/types";

export async function runDiagnostics(): Promise<DiagnosticsReport> {
  const isBrave = !!(navigator as unknown as { brave?: { isBrave?: () => Promise<boolean> } })?.brave;
  const isGmail = window.location.hostname.includes("mail.google.com");

  const compose = queryWithFallback<HTMLElement>(document, "composeView");
  const sendBtn = compose ? queryWithFallback<HTMLElement>(compose, "sendButton") : null;
  const subject = compose ? queryWithFallback<HTMLInputElement>(compose, "subjectInput") : null;
  const recipEls = compose ? compose.querySelectorAll('span[email], [data-hovercard-id*="@"]') : [];

  let backendReachable = false;
  let lastError: string | undefined;

  const settings = await getSettings();
  try {
    const res = await fetch(`${settings.apiBaseUrl}/health`);
    backendReachable = res.ok;
  } catch (err: unknown) {
    lastError = err instanceof Error ? err.message : String(err);
  }

  const report: DiagnosticsReport = {
    braveDetected: isBrave,
    gmailDetected: isGmail,
    composeDetected: !!compose,
    sendButtonDetected: !!sendBtn,
    recipientsCount: recipEls.length,
    subjectDetected: !!subject,
    backendReachable,
    lastError,
    timestamp: new Date().toISOString(),
    selectorStats: selectorDiagnostics,
  };

  await saveDiagnostics(report);
  return report;
}

export async function showDebuggerModal(): Promise<void> {
  const existing = document.getElementById("pm-debugger-modal");
  if (existing) {
    existing.remove();
    return;
  }

  const report = await runDiagnostics();

  const modal = document.createElement("div");
  modal.id = "pm-debugger-modal";
  modal.style.position = "fixed";
  modal.style.bottom = "20px";
  modal.style.right = "20px";
  modal.style.width = "380px";
  modal.style.backgroundColor = "#ffffff";
  modal.style.boxShadow = "0 8px 24px rgba(0,0,0,0.2)";
  modal.style.borderRadius = "8px";
  modal.style.border = "1px solid #dadce0";
  modal.style.zIndex = "999999";
  modal.style.fontFamily = "Google Sans, Roboto, monospace, sans-serif";
  modal.style.fontSize = "13px";
  modal.style.padding = "16px";
  modal.style.color = "#202124";

  const renderStatus = (ok: boolean, label: string) => `
    <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
      <span>${label}:</span>
      <span style="font-weight: bold; color: ${ok ? "#1e8e3e" : "#d93025"};">
        ${ok ? "✓ DETECTED" : "✗ MISSING"}
      </span>
    </div>
  `;

  modal.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #dadce0; padding-bottom: 8px; margin-bottom: 12px;">
      <h3 style="margin: 0; font-size: 15px; color: #1a73e8;">Personal Mailtrack Debugger</h3>
      <button id="pm-dbg-close" style="background:none; border:none; cursor:pointer; font-size: 16px;">✕</button>
    </div>
    ${renderStatus(report.braveDetected, "Brave Browser")}
    ${renderStatus(report.gmailDetected, "Gmail Web")}
    ${renderStatus(report.composeDetected, "Active Compose")}
    ${renderStatus(report.sendButtonDetected, "Send Button")}
    ${renderStatus(report.recipientsCount > 0, `Recipients (${report.recipientsCount})`)}
    ${renderStatus(report.subjectDetected, "Subject Input")}
    ${renderStatus(report.backendReachable, "Backend Health (/health)")}
    ${report.lastError ? `<div style="color: #d93025; font-size: 11px; margin-top: 6px;">Error: ${report.lastError}</div>` : ""}
    <div style="margin-top: 12px; font-size: 11px; color: #5f6368; border-top: 1px solid #f1f3f4; padding-top: 8px;">
      Press <b>Ctrl+Shift+D</b> anytime to toggle this diagnostic tool.
    </div>
  `;

  document.body.appendChild(modal);
  document.getElementById("pm-dbg-close")?.addEventListener("click", () => modal.remove());
}
