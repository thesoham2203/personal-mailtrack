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
        <div className="flex flex-wrap items-center gap-2">
          {["", "opened", "unopened", "clicked", "replied", "waiting_on_them"].map((st) => (
            <button
              key={st}
              onClick={() => setFilter(st)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition ${
                filter === st
                  ? "bg-blue-600 text-white font-semibold"
                  : "bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 text-gray-700 dark:text-slate-300 hover:bg-gray-50 dark:hover:bg-slate-800"
              }`}
            >
              {st ? st.replace("_", " ") : "All Emails"}
            </button>
          ))}
        </div>

        <div className="relative w-64">
          <Search className="w-4 h-4 text-gray-400 dark:text-slate-500 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search subject or recipient..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 text-gray-900 dark:text-white rounded-lg focus:outline-none focus:border-blue-500 dark:focus:border-blue-400 placeholder:text-gray-400 dark:placeholder:text-slate-500 transition-colors"
          />
        </div>
      </div>

      {/* Email Table */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-gray-200 dark:border-slate-800 shadow-sm overflow-hidden transition-colors">
        <div className="divide-y divide-gray-100 dark:divide-slate-800/80">
          {loading ? (
            <div className="p-8 text-center text-sm text-gray-400 dark:text-slate-500">Loading emails...</div>
          ) : filteredEmails.length === 0 ? (
            <div className="p-8 text-center text-sm text-gray-400 dark:text-slate-500">No tracked emails match the criteria.</div>
          ) : (
            filteredEmails.map((em) => {
              const dateStr = new Date(em.sent_at).toLocaleDateString([], {
                month: "short",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit",
              });

              return (
                <div key={em.id} className="p-4 hover:bg-gray-50 dark:hover:bg-slate-800/50 flex items-center justify-between transition gap-4">
                  <div className="flex items-center gap-4 min-w-0">
                    {/* Status Checkmark Badge */}
                    <div className="flex-shrink-0 text-base font-bold">
                      {em.is_hot ? (
                        <span className="text-amber-600 dark:text-amber-400" title="🔥 Hot Conversation">
                          🔥✓✓
                        </span>
                      ) : em.has_replied ? (
                        <span className="text-purple-600 dark:text-purple-400" title="↩ Replied">
                          ↩✓✓
                        </span>
                      ) : em.click_count > 0 ? (
                        <span className="text-blue-600 dark:text-blue-400" title="↗ Link Clicked">
                          ↗✓✓
                        </span>
                      ) : (em.human_open_count ?? 0) > 0 ? (
                        <span className="text-emerald-600 dark:text-emerald-400" title={`✓✓ Human Opened (${em.human_open_count} verified opens)`}>
                          ✓✓
                        </span>
                      ) : em.open_count > 0 ? (
                        <span className="text-amber-500 dark:text-amber-400 font-mono text-sm" title={`~✓ Non-human / Bot prefetch only (${em.open_count} raw opens)`}>
                          ~✓
                        </span>
                      ) : (
                        <span className="text-gray-400 dark:text-slate-500" title="✓ Sent (Unopened)">
                          ✓
                        </span>
                      )}
                    </div>

                    {/* Email Subject & Recipients */}
                    <div className="min-w-0">
                      <div className="text-sm font-semibold text-gray-900 dark:text-white truncate">
                        {em.subject || "(No Subject)"}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-slate-400 mt-0.5 truncate">
                        To: {em.recipients.map((r: any) => r.email).join(", ")}
                      </div>
                    </div>
                  </div>

                  {/* Stats and Certificate Action */}
                  <div className="flex items-center gap-4 flex-shrink-0">
                    <div className="text-right text-xs">
                      <div className="font-semibold text-gray-700 dark:text-slate-300">
                        {em.human_open_count ?? 0} {em.human_open_count === 1 ? "human open" : "human opens"}
                        {em.open_count > (em.human_open_count ?? 0) && (
                          <span className="text-gray-400 dark:text-slate-500 font-normal"> ({em.open_count} raw)</span>
                        )}
                        {" · "}{em.click_count} clicks
                      </div>
                      <div className="text-gray-400 dark:text-slate-500 text-[11px]">{dateStr}</div>
                    </div>

                    <button
                      onClick={() => viewCertificate(em.id)}
                      title="View Certified Delivery Evidence Report"
                      className="p-1.5 text-gray-500 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-slate-800 rounded-lg transition"
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
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-lg w-full border border-gray-200 dark:border-slate-800 shadow-2xl overflow-hidden transition-colors">
            <div className="p-6 border-b border-gray-100 dark:border-slate-800 flex justify-between items-center">
              <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400 font-bold">
                <Award className="w-5 h-5" />
                <span>Certified Delivery Evidence</span>
              </div>
              <button onClick={() => setSelectedCert(null)} className="text-gray-400 dark:text-slate-500 hover:text-gray-600 dark:hover:text-slate-300">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-4 text-xs">
              <div className="bg-gray-50 dark:bg-slate-800/80 p-3 rounded-lg space-y-1 font-mono text-[11px] text-gray-800 dark:text-slate-200 border border-gray-100 dark:border-slate-700/60">
                <div><b>Certificate ID:</b> {selectedCert.certificate_id}</div>
                <div><b>Generated:</b> {selectedCert.generated_at}</div>
                <div><b>Subject:</b> {selectedCert.email.subject}</div>
                <div><b>Sent At:</b> {selectedCert.email.sent_at}</div>
              </div>

              <div className="font-semibold text-gray-900 dark:text-white">Recipient Tracking Audit Trail:</div>
              <div className="space-y-2">
                {selectedCert.recipients.map((r: any, idx: number) => (
                  <div key={idx} className="p-3 border border-gray-200 dark:border-slate-800 rounded-lg space-y-1 text-gray-700 dark:text-slate-300">
                    <div className="font-semibold text-blue-700 dark:text-blue-400">{r.email}</div>
                    <div>First Open: {r.first_open_at || "Never"}</div>
                    <div>Total Opens: {r.human_open_count}</div>
                    <div>Link Clicks: {r.click_count}</div>
                    <div>Reply Received: {r.reply_received_at || "None"}</div>
                  </div>
                ))}
              </div>

              <div className="text-[10px] italic bg-amber-50 dark:bg-amber-950/40 p-2.5 rounded border border-amber-100 dark:border-amber-900/60 text-amber-800 dark:text-amber-300">
                {selectedCert.disclaimer}
              </div>
            </div>

            <div className="p-4 bg-gray-50 dark:bg-slate-800/60 border-t border-gray-100 dark:border-slate-800 flex justify-end">
              <button
                onClick={() => {
                  const blob = new Blob([JSON.stringify(selectedCert, null, 2)], { type: "application/json" });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement("a");
                  a.href = url;
                  a.download = `certificate_${selectedCert.certificate_id}.json`;
                  a.click();
                }}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-sm"
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
