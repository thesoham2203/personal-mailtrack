/**
 * chrome.storage.local wrapper for persistent extension state.
 */

import { DEFAULT_SETTINGS, STORAGE_KEYS } from "./constants";
import { TrackingSettings, DiagnosticsReport } from "./types";

export async function getSettings(): Promise<TrackingSettings> {
  return new Promise((resolve) => {
    chrome.storage.local.get([STORAGE_KEYS.SETTINGS], (result) => {
      resolve({ ...DEFAULT_SETTINGS, ...(result[STORAGE_KEYS.SETTINGS] || {}) });
    });
  });
}

export async function saveSettings(settings: Partial<TrackingSettings>): Promise<void> {
  const current = await getSettings();
  const updated = { ...current, ...settings };
  return new Promise((resolve) => {
    chrome.storage.local.set({ [STORAGE_KEYS.SETTINGS]: updated }, () => {
      resolve();
    });
  });
}

export async function saveDiagnostics(report: DiagnosticsReport): Promise<void> {
  return new Promise((resolve) => {
    chrome.storage.local.set({ [STORAGE_KEYS.DIAGNOSTICS]: report }, () => resolve());
  });
}

export async function getDiagnostics(): Promise<DiagnosticsReport | null> {
  return new Promise((resolve) => {
    chrome.storage.local.get([STORAGE_KEYS.DIAGNOSTICS], (result) => {
      resolve(result[STORAGE_KEYS.DIAGNOSTICS] || null);
    });
  });
}
