import React, { useEffect, useState } from "react";
import { fetchContacts, fetchContactDetail } from "../services/api";
import { Search, User, X, Eye, MousePointer, CornerUpLeft } from "lucide-react";

export const ContactsPage: React.FC = () => {
  const [contacts, setContacts] = useState<any[]>([]);
  const [search, setSearch] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [selectedContact, setSelectedContact] = useState<any>(null);

  const loadContacts = async () => {
    try {
      const data = await fetchContacts(search);
      setContacts(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadContacts();
  }, [search]);

  const openContact = async (id: string) => {
    try {
      const detail = await fetchContactDetail(id);
      setSelectedContact(detail);
    } catch (err) {
      alert("Could not load contact details.");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-lg font-bold text-gray-900">Personal Contact CRM</h2>
          <p className="text-xs text-gray-500">Heuristic engagement scores and interaction history for your contacts.</p>
        </div>

        <div className="relative w-64">
          <Search className="w-4 h-4 text-gray-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search contacts..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-white border border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>

      {/* Contacts Table */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden divide-y divide-gray-100">
        {loading ? (
          <div className="p-8 text-center text-sm text-gray-400">Loading contacts...</div>
        ) : contacts.length === 0 ? (
          <div className="p-8 text-center text-sm text-gray-400">No contacts found.</div>
        ) : (
          contacts.map((c) => (
            <div
              key={c.id}
              onClick={() => openContact(c.id)}
              className="p-4 hover:bg-gray-50 flex items-center justify-between cursor-pointer transition"
            >
              <div className="flex items-center gap-3.5">
                <div className="w-9 h-9 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-xs">
                  {c.name ? c.name[0].toUpperCase() : c.email[0].toUpperCase()}
                </div>
                <div>
                  <div className="text-sm font-semibold text-gray-900">{c.name || c.email}</div>
                  <div className="text-xs text-gray-500">{c.email} {c.company ? `· ${c.company}` : ""}</div>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <span
                  className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold ${
                    c.status === "Hot"
                      ? "bg-amber-100 text-amber-800"
                      : c.status === "Warm"
                      ? "bg-emerald-100 text-emerald-800"
                      : "bg-gray-100 text-gray-600"
                  }`}
                >
                  {c.status} ({c.engagement_score} pts)
                </span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Contact Timeline Drawer */}
      {selectedContact && (
        <div className="fixed inset-0 bg-black/30 backdrop-blur-sm z-50 flex justify-end">
          <div className="bg-white w-full max-w-md h-full shadow-2xl p-6 flex flex-col justify-between overflow-y-auto">
            <div className="space-y-6">
              <div className="flex justify-between items-start border-b border-gray-100 pb-4">
                <div className="flex items-center gap-3">
                  <div className="w-11 h-11 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-base">
                    {selectedContact.name ? selectedContact.name[0].toUpperCase() : selectedContact.email[0].toUpperCase()}
                  </div>
                  <div>
                    <h3 className="font-bold text-gray-900 text-base">{selectedContact.name || selectedContact.email}</h3>
                    <p className="text-xs text-gray-500">{selectedContact.email}</p>
                  </div>
                </div>
                <button onClick={() => setSelectedContact(null)} className="text-gray-400 hover:text-gray-600">
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Engagement Status Card */}
              <div className="bg-gray-50 p-4 rounded-xl border border-gray-200 flex justify-between items-center text-xs">
                <div>
                  <span className="text-gray-400 block font-medium">Engagement Status</span>
                  <span className="font-bold text-gray-900 text-sm">{selectedContact.status}</span>
                </div>
                <div>
                  <span className="text-gray-400 block font-medium">Heuristic Score</span>
                  <span className="font-bold text-blue-600 text-sm">{selectedContact.engagement_score} points</span>
                </div>
              </div>

              {/* Chronological Timeline */}
              <div>
                <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-3">
                  Interaction History Timeline
                </h4>
                <div className="space-y-3">
                  {selectedContact.timeline.length === 0 ? (
                    <div className="text-xs text-gray-400">No interaction events yet.</div>
                  ) : (
                    selectedContact.timeline.map((item: any) => {
                      const date = new Date(item.occurred_at).toLocaleString([], {
                        month: "short",
                        day: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      });
                      const isClick = item.event_type === "email.clicked";
                      const isReply = item.event_type === "email.replied";

                      return (
                        <div key={item.id} className="flex items-start gap-2.5 text-xs p-2.5 rounded-lg border border-gray-100 bg-white">
                          <div className="p-1.5 rounded bg-gray-50 text-blue-600">
                            {isReply ? <CornerUpLeft className="w-3.5 h-3.5" /> : isClick ? <MousePointer className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                          </div>
                          <div className="flex-1">
                            <div className="font-medium text-gray-900">
                              {item.event_type === "email.opened" ? "Opened email" : isClick ? "Clicked tracked link" : "Replied to email"}
                            </div>
                            <div className="text-gray-400 text-[11px]">{date}</div>
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
              </div>
            </div>

            <button
              onClick={() => setSelectedContact(null)}
              className="w-full py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-xs font-semibold"
            >
              Close Drawer
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
