/**
 * Centralized Gmail DOM selectors with semantic fallback chains and diagnostic logging.
 * (PRD Section 15, 86 & Requirement 35)
 */

export interface SelectorMatchStats {
  matches: number;
  lastSelector: string;
  lastChecked: string;
}

export const selectorDiagnostics: Record<string, SelectorMatchStats> = {};

export const SELECTORS = {
  // Compose Dialogs
  composeView: [
    'div[role="dialog"][aria-label*="Compose"]',
    'div[role="dialog"][aria-label*="New Message"]',
    'div.M9', // standard Gmail compose container
    'div[role="region"][aria-label*="Compose"]',
  ],

  // Send Button
  sendButton: [
    'div[role="button"][data-tooltip*="Send"]',
    'div[role="button"][aria-label*="Send"]',
    'div.T-I.J-J5-Ji.aoO.v7.T-I-atl.L3', // primary Send button class
    'div[data-tooltip*="Send ‪(Ctrl-Enter)‬"]',
  ],

  // Subject Input
  subjectInput: [
    'input[name="subjectbox"]',
    'input[aria-label="Subject"]',
    'input[placeholder="Subject"]',
  ],

  // Editable Body
  messageBody: [
    'div[role="textbox"][aria-label*="Message Body"]',
    'div[g_editable="true"]',
    'div.Am.Al.editable',
  ],

  // Recipients
  recipientChips: [
    'span[email]',
    'div[data-hovercard-id]',
    'span[data-hovercard-id]',
    'input[aria-label*="To"]',
  ],

  // Bottom Toolbar in Compose (beside Send button)
  composeToolbar: [
    'tr.btC', // Gmail bottom row containing send button & formatting bar
    'div.IZ', // Send button container
    'td.gU.Up', // Action buttons row
  ],

  // Sent/Inbox Email Rows
  messageRows: [
    'tr.zA', // Standard table row for emails in Gmail lists
    'div[role="main"] tr[role="row"]',
  ],

  // Subject/Snippet in List Row
  rowSubject: [
    'span.bog', // Subject span
    'span[data-thread-id]',
  ],

  // Date column in List Row
  rowDate: [
    'td.xW', // Date table cell
    'span.bq9',
  ],
};

/**
 * Finds the first matching element using fallback selector chain, tracking diagnostic stats.
 */
export function queryWithFallback<T extends Element = HTMLElement>(
  parent: Document | Element,
  selectorKey: keyof typeof SELECTORS
): T | null {
  const chain = SELECTORS[selectorKey];
  for (const selector of chain) {
    try {
      const el = parent.querySelector(selector);
      if (el) {
        selectorDiagnostics[selectorKey] = {
          matches: (selectorDiagnostics[selectorKey]?.matches || 0) + 1,
          lastSelector: selector,
          lastChecked: new Date().toISOString(),
        };
        return el as T;
      }
    } catch (err) {
      // Ignore invalid selector syntax
    }
  }

  // Not found in any fallback
  selectorDiagnostics[selectorKey] = {
    matches: selectorDiagnostics[selectorKey]?.matches || 0,
    lastSelector: "NONE_MATCHED",
    lastChecked: new Date().toISOString(),
  };
  return null;
}

/**
 * Finds all matching elements using the first selector in the chain that returns items.
 */
export function queryAllWithFallback<T extends Element = HTMLElement>(
  parent: Document | Element,
  selectorKey: keyof typeof SELECTORS
): T[] {
  const chain = SELECTORS[selectorKey];
  for (const selector of chain) {
    try {
      const els = parent.querySelectorAll(selector);
      if (els.length > 0) {
        selectorDiagnostics[selectorKey] = {
          matches: (selectorDiagnostics[selectorKey]?.matches || 0) + els.length,
          lastSelector: selector,
          lastChecked: new Date().toISOString(),
        };
        return Array.from(els) as T[];
      }
    } catch (err) {
      // Ignore
    }
  }
  return [];
}
