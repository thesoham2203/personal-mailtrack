import React, { useEffect, useState } from "react";
import { fetchEmails, fetchCertificate } from "../services/api";
import { Search, Award, Download, X } from "lucide-react";

export const EmailsPage: React.FC = () => {
  const [emails, setEmails] = useState<any[]>([]);
  const [filter, setFilter] = useState<string>("");
  const [search, setSearch] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [selectedCert, setSelectedCert] = useState<any>(null);

  const loadEmails = async () => {
    setLoading(true);
    try {
      const data = await fetchEmails(filter || undefined);
      setEmails(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEmails();
  }, [filter]);

  const viewCertificate = async (emailId: string) => {
    try {
      const cert = await fetchCertificate(emailId);
      setSelectedCert(cert);
    } catch (err) {
      alert("Could not load certificate.");
    }
  };

  const filteredEmails = emails.filter((em) => {
    if (!search) return true;
    const s = search.toLowerCase();
    const subjMatch = (em.subject || "").toLowerCase().includes(s);
    const recipMatch = em.recipients.some((r: any) => r.email.toLowerCase().includes(s));
    return subjMatch || recipMatch;
  });

  return (
    <div className="space-y-6">
      {/* Header & Filter Controls */}
      <div className="flex flex-wrap justify-between items-center gap-4">
        <div className="flex items-center gap-2">
          {["", "opened", "unopened", "clicked", "replied", "waiting_on_them"].map((st) => (
            <button
              key={st}
              onClick={() => setFilter(st)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition ${
                filter === st
                  ? "bg-blue-600 text-white font-semibold"
                  : "bg-white border border-gray-200 text-gray-700 hover:bg-gray-50"
              }`}
            >
              {st ? st.replace("_", " ") : "All Emails"}
            </button>
          ))}
        </div>

        <div className="relative w-64">
          <Search className="w-4 h-4 text-gray-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search subject or recipient..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-white border border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>

      {/* Email Table */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="divide-y divide-gray-100">
          {loading ? (
            <div className="p-8 text-center text-sm text-gray-400">Loading emails...</div>
          ) : filteredEmails.length === 0 ? (
            <div className="p-8 text-center text-sm text-gray-400">No tracked emails match the criteria.</div>
          ) : (
            filteredEmails.map((em) => {
              const dateStr = new Date(em.sent_at).toLocaleDateString([], {
                month: "short",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit",
              });

              return (
                <div key={em.id} className="p-4 hover:bg-gray-50 flex items-center justify-between transition gap-4">
                  <div className="flex items-center gap-4 min-w-0">
                    {/* Status Checkmark Badge */}
                    <div className="flex-shrink-0 text-base font-bold">
                      {em.is_hot ? (
                        <span className="text-amber-600" title="🔥 Hot Conversation">
                          🔥✓✓
                        </span>
                      ) : em.has_replied ? (
                        <span className="text-purple-600" title="↩ Replied">
                          ↩✓✓
                        </span>
                      ) : em.click_count > 0 ? (
                        <span className="text-blue-600" title="↗ Link Clicked">
                          ↗✓✓
                        </span>
                      ) : em.open_count > 0 ? (
                        <span className="text-emerald-600" title="✓✓ Opened">
                          ✓✓
                        </span>
                      ) : (
                        <span className="text-gray-400" title="✓ Sent (Unopened)">
                          ✓
                        </span>
                      )}
                    </div>

                    {/* Email Subject & Recipients */}
                    <div className="min-w-0">
                      <div className="text-sm font-semibold text-gray-900 truncate">
                        {em.subject || "(No Subject)"}
                      </div>
                      <div className="text-xs text-gray-500 mt-0.5 truncate">
                        To: {em.recipients.map((r: any) => r.email).join(", ")}
                      </div>
                    </div>
                  </div>

                  {/* Stats and Certificate Action */}
                  <div className="flex items-center gap-4 flex-shrink-0">
                    <div className="text-right text-xs">
                      <div className="font-semibold text-gray-700">
                        {em.open_count} {em.open_count === 1 ? "open" : "opens"} · {em.click_count} clicks
                      </div>
                      <div className="text-gray-400 text-[11px]">{dateStr}</div>
                    </div>

                    <button
                      onClick={() => viewCertificate(em.id)}
                      title="View Certified Delivery Evidence Report"
                      className="p-1.5 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition"
                    >
                      <Award className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Certificate Modal */}
      {selectedCert && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full border border-gray-200 shadow-xl overflow-hidden">
            <div className="p-6 border-b border-gray-100 flex justify-between items-center">
              <div className="flex items-center gap-2 text-blue-600 font-bold">
                <Award className="w-5 h-5" />
                <span>Certified Delivery Evidence</span>
              </div>
              <button onClick={() => setSelectedCert(null)} className="text-gray-400 hover:text-gray-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-4 text-xs">
              <div className="bg-gray-50 p-3 rounded-lg space-y-1 font-mono text-[11px]">
                <div><b>Certificate ID:</b> {selectedCert.certificate_id}</div>
                <div><b>Generated:</b> {selectedCert.generated_at}</div>
                <div><b>Subject:</b> {selectedCert.email.subject}</div>
                <div><b>Sent At:</b> {selectedCert.email.sent_at}</div>
              </div>

              <div className="font-semibold text-gray-900">Recipient Tracking Audit Trail:</div>
              <div className="space-y-2">
                {selectedCert.recipients.map((r: any, idx: number) => (
                  <div key={idx} className="p-3 border border-gray-200 rounded-lg space-y-1">
                    <div className="font-semibold text-blue-700">{r.email}</div>
                    <div>First Open: {r.first_open_at || "Never"}</div>
                    <div>Total Opens: {r.human_open_count}</div>
                    <div>Link Clicks: {r.click_count}</div>
                    <div>Reply Received: {r.reply_received_at || "None"}</div>
                  </div>
                ))}
              </div>

              <div className="text-[10px] text-gray-400 italic bg-amber-50 p-2.5 rounded border border-amber-100 text-amber-800">
                {selectedCert.disclaimer}
              </div>
            </div>

            <div className="p-4 bg-gray-50 border-t border-gray-100 flex justify-end">
              <button
                onClick={() => {
                  const blob = new Blob([JSON.stringify(selectedCert, null, 2)], { type: "application/json" });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement("a");
                  a.href = url;
                  a.download = `certificate_${selectedCert.certificate_id}.json`;
                  a.click();
                }}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold"
              >
                <Download className="w-3.5 h-3.5" /> Download Evidence Report
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
