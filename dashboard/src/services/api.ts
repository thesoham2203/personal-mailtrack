/**
 * Typed API Client for Personal Mailtrack Backend.
 */

export const API_BASE =
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.PROD ? "https://personal-mailtrack-api.onrender.com" : "");

export async function fetchSummary(days = 30) {
  const res = await fetch(`${API_BASE}/api/v1/analytics/summary?days=${days}`);
  if (!res.ok) throw new Error("Failed to fetch analytics summary");
  return res.json();
}

export async function fetchActivity(limit = 50, eventType?: string) {
  const url = `${API_BASE}/api/v1/analytics/activity?limit=${limit}${eventType ? `&event_type=${eventType}` : ""}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch activity");
  return res.json();
}

export async function fetchEmails(filterStatus?: string) {
  const url = `${API_BASE}/api/v1/emails?limit=100${filterStatus ? `&filter_status=${filterStatus}` : ""}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch emails");
  return res.json();
}

export async function fetchContacts(search?: string) {
  const url = `${API_BASE}/api/v1/contacts?limit=100${search ? `&search=${encodeURIComponent(search)}` : ""}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch contacts");
  return res.json();
}

export async function fetchContactDetail(contactId: string) {
  const res = await fetch(`${API_BASE}/api/v1/contacts/${contactId}`);
  if (!res.ok) throw new Error("Failed to fetch contact details");
  return res.json();
}

export async function fetchCampaigns() {
  const res = await fetch(`${API_BASE}/api/v1/campaigns`);
  if (!res.ok) throw new Error("Failed to fetch campaigns");
  return res.json();
}

export async function createCampaign(data: { name: string; subject: string; body_html: string; recipients: { email: string; data?: any }[] }) {
  const res = await fetch(`${API_BASE}/api/v1/campaigns`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create campaign");
  return res.json();
}

export async function sendCampaign(campaignId: string) {
  const res = await fetch(`${API_BASE}/api/v1/campaigns/${campaignId}/send`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to send campaign");
  return res.json();
}

export async function fetchTemplates() {
  const res = await fetch(`${API_BASE}/api/v1/templates`);
  if (!res.ok) throw new Error("Failed to fetch templates");
  return res.json();
}

export async function createTemplate(data: { title: string; subject: string; body_html: string; category?: string }) {
  const res = await fetch(`${API_BASE}/api/v1/templates`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create template");
  return res.json();
}

export async function fetchDocuments() {
  const res = await fetch(`${API_BASE}/api/v1/documents`);
  if (!res.ok) throw new Error("Failed to fetch documents");
  return res.json();
}

export async function uploadDocument(file: File, title?: string) {
  const formData = new FormData();
  formData.append("file", file);
  if (title) formData.append("title", title);
  const res = await fetch(`${API_BASE}/api/v1/documents`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error("Failed to upload document");
  return res.json();
}

export async function createDocumentShare(docId: string, payload: { recipient_email?: string; expires_in_days?: number; download_allowed?: boolean; watermark_text?: string }) {
  const res = await fetch(`${API_BASE}/api/v1/documents/${docId}/shares`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to create document share");
  return res.json();
}

export async function fetchDocumentAnalytics(docId: string) {
  const res = await fetch(`${API_BASE}/api/v1/documents/${docId}/analytics`);
  if (!res.ok) throw new Error("Failed to fetch document analytics");
  return res.json();
}

export async function fetchDoctorDiagnostics() {
  const res = await fetch(`${API_BASE}/api/v1/diagnostics/doctor`);
  if (!res.ok) throw new Error("Failed to fetch diagnostics");
  return res.json();
}

export async function fetchCertificate(emailId: string) {
  const res = await fetch(`${API_BASE}/api/v1/analytics/certificate/${emailId}`);
  if (!res.ok) throw new Error("Failed to fetch certificate");
  return res.json();
}
