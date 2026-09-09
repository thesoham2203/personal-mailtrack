import React, { useEffect, useState } from "react";
import { fetchActivity, fetchSummary } from "../services/api";
import { Eye, MousePointer, CornerUpLeft, FileText, CheckCircle2, ShieldAlert } from "lucide-react";

export const ActivityPage: React.FC = () => {
  const [activities, setActivities] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [filter, setFilter] = useState<string>("all");
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      const [sumData, actData] = await Promise.all([fetchSummary(), fetchActivity(50)]);
      setSummary(sumData);
      setActivities(actData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000); // Live poll every 5s
    return () => clearInterval(interval);
  }, []);

  const filteredActivities = activities.filter((a) => {
    if (filter === "human") return a.event_type === "email.opened" && a.metadata?.classification === "human_likely";
    if (filter === "proxy") return a.event_type === "email.opened" && a.metadata?.classification !== "human_likely";
    if (filter === "clicks") return a.event_type === "email.clicked";
    if (filter === "replies") return a.event_type === "email.replied";
    if (filter === "documents") return a.event_type === "document.viewed";
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Top Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Emails Sent</span>
          <div className="mt-2 text-2xl font-bold text-gray-900">{summary?.total_sent || 0}</div>
          <span className="text-xs text-gray-400 mt-1 block">Last 30 days</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Verified Human Opens</span>
          <div className="mt-2 text-2xl font-bold text-emerald-600">
            {summary?.total_human_opens || 0}
            <span className="text-xs font-normal text-gray-400 ml-2">({summary?.open_rate_percent || 0}%)</span>
          </div>
          <span className="text-xs text-gray-400 mt-1 block">Total raw opens: {summary?.total_raw_opens || 0}</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Link Clicks</span>
          <div className="mt-2 text-2xl font-bold text-blue-600">{summary?.total_clicks || 0}</div>
          <span className="text-xs text-gray-400 mt-1 block">CTR: {summary?.click_rate_percent || 0}%</span>
        </div>

        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Replies Received</span>
          <div className="mt-2 text-2xl font-bold text-purple-600">{summary?.total_replies || 0}</div>
          <span className="text-xs text-gray-400 mt-1 block">Reply rate: {summary?.reply_rate_percent || 0}%</span>
        </div>
      </div>

      {/* Activity Timeline Table */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-gray-200 flex flex-wrap justify-between items-center gap-3">
          <div>
            <h2 className="text-base font-semibold text-gray-900">Live Activity Feed</h2>
            <p className="text-xs text-gray-500">Chronological timeline of all tracked opens, clicks, and views.</p>
          </div>

          <div className="flex gap-2">
            {[
              { id: "all", label: "All Activity" },
              { id: "human", label: "Likely Human Opens" },
              { id: "proxy", label: "Proxy / Prefetch" },
              { id: "clicks", label: "Clicks" },
              { id: "replies", label: "Replies" },
              { id: "documents", label: "PDF Views" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setFilter(tab.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                  filter === tab.id
                    ? "bg-blue-600 text-white"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        <div className="divide-y divide-gray-100">
          {loading ? (
            <div className="p-8 text-center text-sm text-gray-400">Loading timeline...</div>
          ) : filteredActivities.length === 0 ? (
            <div className="p-8 text-center text-sm text-gray-400">
              No matching activity recorded yet. Send a tracked email to get started!
            </div>
          ) : (
            filteredActivities.map((act) => {
              const date = new Date(act.occurred_at).toLocaleString();
              const meta = act.metadata || {};

              let icon = <Eye className="w-4 h-4 text-emerald-600" />;
              let title = `Email opened: "${meta.subject || "No Subject"}"`;
              let sub = meta.recipient_email || "Recipient";

              if (act.event_type === "email.clicked") {
                icon = <MousePointer className="w-4 h-4 text-blue-600" />;
                title = `Link clicked in "${meta.subject || "Email"}"`;
                sub = `Destination: ${meta.destination_url || "Link"}`;
              } else if (act.event_type === "email.replied") {
                icon = <CornerUpLeft className="w-4 h-4 text-purple-600" />;
                title = `Reply received for "${meta.subject || "Email"}"`;
              } else if (act.event_type === "document.viewed") {
                icon = <FileText className="w-4 h-4 text-amber-600" />;
                title = `Document viewed: "${meta.title || "PDF Document"}"`;
              } else if (act.event_type === "email.sent") {
                icon = <CheckCircle2 className="w-4 h-4 text-gray-400" />;
                title = `Tracked email sent: "${meta.subject || "No Subject"}"`;
              }

              const isProxy = meta.classification && meta.classification !== "human_likely";

              return (
                <div key={act.id} className="p-4 hover:bg-gray-50 flex items-center justify-between transition">
                  <div className="flex items-center gap-3.5">
                    <div className="p-2 rounded-lg bg-gray-50 border border-gray-100 flex items-center justify-center">
                      {icon}
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-900 flex items-center gap-2">
                        {title}
                        {isProxy && (
                          <span className="inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200">
                            <ShieldAlert className="w-3 h-3" />
                            {meta.classification === "proxy_likely" ? "Proxy/Prefetch" : "Scanner Bot"}
                          </span>
                        )}
                      </div>
                      <div className="text-xs text-gray-500 mt-0.5">{sub}</div>
                    </div>
                  </div>
                  <div className="text-xs text-gray-400 font-mono">{date}</div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};
