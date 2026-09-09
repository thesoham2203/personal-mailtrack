import React, { useEffect, useState } from "react";
import { fetchEmails } from "../services/api";
import { Flame, Clock, AlertTriangle, Sparkles, Inbox } from "lucide-react";

export const FollowUpPage: React.FC = () => {
  const [emails, setEmails] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<string>("waiting_on_them");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEmails()
      .then(setEmails)
      .finally(() => setLoading(false));
  }, []);

  const now = new Date().getTime();

  // Categorize emails
  const hotEmails = emails.filter((e) => e.is_hot);
  const waitingOnThem = emails.filter((e) => !e.has_replied);
  const noReplyDue = emails.filter((e) => {
    if (e.has_replied) return false;
    const sentTime = new Date(e.sent_at).getTime();
    const hoursElapsed = (now - sentTime) / (1000 * 60 * 60);
    return hoursElapsed >= 48; // 48h default threshold
  });
  const revivedEmails = emails.filter((e) => {
    // If open count > 1 and sent > 7 days ago
    const sentTime = new Date(e.sent_at).getTime();
    return e.open_count > 1 && now - sentTime > 7 * 24 * 60 * 60 * 1000;
  });

  const getListForTab = () => {
    switch (activeTab) {
      case "hot":
        return hotEmails;
      case "waiting_on_them":
        return waitingOnThem;
      case "no_reply":
        return noReplyDue;
      case "revived":
        return revivedEmails;
      default:
        return waitingOnThem;
    }
  };

  const list = getListForTab();

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-bold text-gray-900">Follow-Up Command Center</h2>
        <p className="text-xs text-gray-500">Track who needs a reminder, hot leads, and conversations awaiting action.</p>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-gray-200 pb-3">
        {[
          { id: "waiting_on_them", label: "Waiting on Them", icon: Clock, count: waitingOnThem.length },
          { id: "hot", label: "Hot Conversations", icon: Flame, count: hotEmails.length },
          { id: "no_reply", label: "No-Reply Overdue (48h+)", icon: AlertTriangle, count: noReplyDue.length },
          { id: "revived", label: "Recently Revived", icon: Sparkles, count: revivedEmails.length },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition ${
                isActive
                  ? "bg-blue-600 text-white shadow-sm"
                  : "bg-white border border-gray-200 text-gray-700 hover:bg-gray-50"
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
              <span className={`px-1.5 py-0.5 rounded-full text-[10px] ${isActive ? "bg-white/20 text-white" : "bg-gray-100 text-gray-600"}`}>
                {tab.count}
              </span>
            </button>
          );
        })}
      </div>

      {/* List */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden divide-y divide-gray-100">
        {loading ? (
          <div className="p-8 text-center text-sm text-gray-400">Loading follow-ups...</div>
        ) : list.length === 0 ? (
          <div className="p-8 text-center text-sm text-gray-400">
            No emails in this queue! You're all caught up.
          </div>
        ) : (
          list.map((em) => {
            const dateStr = new Date(em.sent_at).toLocaleDateString([], {
              month: "short",
              day: "numeric",
              hour: "2-digit",
              minute: "2-digit",
            });

            return (
              <div key={em.id} className="p-4 hover:bg-gray-50 flex items-center justify-between transition">
                <div>
                  <div className="text-sm font-semibold text-gray-900">{em.subject || "(No Subject)"}</div>
                  <div className="text-xs text-gray-500 mt-0.5">
                    To: {em.recipients.map((r: any) => r.email).join(", ")} · Sent {dateStr}
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <div className="text-xs text-right">
                    <span className="font-semibold text-emerald-600">{em.open_count} opens</span>
                    <span className="text-gray-400 block text-[11px]">{em.click_count} clicks</span>
                  </div>
                  <a
                    href="https://mail.google.com"
                    target="_blank"
                    rel="noreferrer"
                    className="px-3 py-1.5 bg-gray-100 hover:bg-blue-50 hover:text-blue-600 rounded-lg text-xs font-medium text-gray-700 transition"
                  >
                    Reply in Gmail
                  </a>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
