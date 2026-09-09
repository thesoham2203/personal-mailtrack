/**
 * Shared TypeScript interfaces for Personal Mailtrack Extension.
 */

export interface TrackingSettings {
  apiBaseUrl: string;
  trackingBaseUrl: string;
  trackingEnabled: boolean;
  linkTrackingEnabled: boolean;
  prepareTimeoutMs: number;
  desktopNotifications: boolean;
}

export interface RecipientInfo {
  email: string;
  name?: string;
  recipient_type: "to" | "cc" | "bcc";
}

export interface EmailRegisterPayload {
  subject: string;
  recipients: RecipientInfo[];
  links: string[];
  gmail_message_id?: string;
  gmail_thread_id?: string;
}

export interface TrackedLinkMap {
  original_url: string;
  tracked_url: string;
}

export interface EmailRegisterResponse {
  tracked_email_id: string;
  public_id: string;
  pixel_url: string;
  links: TrackedLinkMap[];
}

export interface DiagnosticsReport {
  braveDetected: boolean;
  gmailDetected: boolean;
  composeDetected: boolean;
  sendButtonDetected: boolean;
  recipientsCount: number;
  subjectDetected: boolean;
  backendReachable: boolean;
  lastError?: string;
  timestamp: string;
  selectorStats: Record<string, { matches: number; lastSelector: string }>;
}

export interface ActivityEventSummary {
  id: string;
  event_type: string;
  occurred_at: string;
  metadata?: {
    subject?: string;
    recipient_email?: string;
    destination_url?: string;
    classification?: string;
  };
}
