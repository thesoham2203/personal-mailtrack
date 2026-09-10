/**
 * chrome.storage.local wrapper for persistent extension state.
 */

import { DEFAULT_SETTINGS, STORAGE_KEYS } from "./constants";
import { TrackingSettings, DiagnosticsReport } from "./types";

export async function getSettings(): Promise<TrackingSettings> {
  return new Promise((resolve) => {
    try {
      if (typeof chrome === "undefined" || !chrome?.storage?.local) {
        resolve({ ...DEFAULT_SETTINGS });
        return;
      }
      chrome.storage.local.get([STORAGE_KEYS.SETTINGS], (result) => {
        if (chrome.runtime?.lastError || !result) {
          resolve({ ...DEFAULT_SETTINGS });
          return;
        }
        resolve({ ...DEFAULT_SETTINGS, ...(result[STORAGE_KEYS.SETTINGS] || {}) });
      });
    } catch {
      resolve({ ...DEFAULT_SETTINGS });
    }
  });
}

export async function saveSettings(settings: Partial<TrackingSettings>): Promise<void> {
  try {
    if (typeof chrome === "undefined" || !chrome?.storage?.local) return;
    const current = await getSettings();
    const updated = { ...current, ...settings };
    return new Promise((resolve) => {
      chrome.storage.local.set({ [STORAGE_KEYS.SETTINGS]: updated }, () => {
        resolve();
      });
    });
  } catch {
    // Fail silent
  }
}

export async function saveDiagnostics(report: DiagnosticsReport): Promise<void> {
  return new Promise((resolve) => {
    try {
      if (typeof chrome === "undefined" || !chrome?.storage?.local) {
        resolve();
        return;
      }
      chrome.storage.local.set({ [STORAGE_KEYS.DIAGNOSTICS]: report }, () => resolve());
    } catch {
      resolve();
    }
  });
}

export async function getDiagnostics(): Promise<DiagnosticsReport | null> {
  return new Promise((resolve) => {
    try {
      if (typeof chrome === "undefined" || !chrome?.storage?.local) {
        resolve(null);
        return;
      }
      chrome.storage.local.get([STORAGE_KEYS.DIAGNOSTICS], (result) => {
        if (chrome.runtime?.lastError || !result) {
          resolve(null);
          return;
        }
        resolve(result[STORAGE_KEYS.DIAGNOSTICS] || null);
      });
    } catch {
      resolve(null);
    }
  });
}

