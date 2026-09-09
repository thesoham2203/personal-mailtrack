import React, { useEffect, useState } from "react";
import { fetchCampaigns, createCampaign, sendCampaign } from "../services/api";
import { Plus, Send, CheckCircle, Clock } from "lucide-react";

export const CampaignsPage: React.FC = () => {
  const [campaigns, setCampaigns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  // Form states
  const [name, setName] = useState("");
  const [subject, setSubject] = useState("Hi {{first_name | fallback: 'there'}}, quick update");
  const [bodyHtml, setBodyHtml] = useState("<p>Hello {{first_name}},</p><p>Wanted to share our latest notes: <a href='https://example.com/notes'>Click here</a>.</p>");
  const [recipientsText, setRecipientsText] = useState("alice@example.com, Alice\nbob@example.com, Bob");

  const loadCampaigns = async () => {
    try {
      const data = await fetchCampaigns();
      setCampaigns(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCampaigns();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const lines = recipientsText.split("\n").filter((l) => l.trim().length > 0);
    const recipients = lines.map((line) => {
      const [email, nameVal] = line.split(",").map((s) => s.trim());
      return {
        email,
        data: { first_name: nameVal || email.split("@")[0] },
      };
    });

    try {
      await createCampaign({
        name,
        subject,
        body_html: bodyHtml,
        recipients,
      });
      setShowModal(false);
      setName("");
      loadCampaigns();
    } catch (err) {
      alert("Failed to create campaign.");
    }
  };

  const handleSend = async (id: string) => {
    if (!confirm("Send personalized emails with individualized tracking to all recipients?")) return;
    try {
      await sendCampaign(id);
      loadCampaigns();
    } catch (err) {
      alert("Failed to send campaign.");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-lg font-bold text-gray-900">Mail-Merge Campaigns</h2>
          <p className="text-xs text-gray-500">Send personalized, individualized tracked campaigns with zero spam risk.</p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-sm transition"
        >
          <Plus className="w-4 h-4" /> Create Campaign
        </button>
      </div>

      {/* Campaigns List */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden divide-y divide-gray-100">
        {loading ? (
          <div className="p-8 text-center text-sm text-gray-400">Loading campaigns...</div>
        ) : campaigns.length === 0 ? (
          <div className="p-8 text-center text-sm text-gray-400">No campaigns created yet. Click above to create one!</div>
        ) : (
          campaigns.map((c) => (
            <div key={c.id} className="p-5 flex items-center justify-between hover:bg-gray-50 transition">
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-semibold text-gray-900">{c.name}</h3>
                  <span
                    className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                      c.status === "completed"
                        ? "bg-emerald-100 text-emerald-800"
                        : c.status === "sending"
                        ? "bg-blue-100 text-blue-800"
                        : "bg-gray-100 text-gray-600"
                    }`}
                  >
                    {c.status}
                  </span>
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Subject: <i>"{c.subject}"</i> · {c.total_recipients} recipients
                </div>
              </div>

              <div className="flex items-center gap-3">
                {c.status === "draft" && (
                  <button
                    onClick={() => handleSend(c.id)}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-sm transition"
                  >
                    <Send className="w-3.5 h-3.5" /> Dispatch
                  </button>
                )}
                {c.status === "completed" && (
                  <div className="flex items-center gap-1 text-emerald-600 text-xs font-medium">
                    <CheckCircle className="w-4 h-4" /> Sent
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* New Campaign Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-xl w-full border border-gray-200 shadow-2xl p-6">
            <h3 className="text-base font-bold text-gray-900 mb-4">Create Mail-Merge Campaign</h3>
            <form onSubmit={handleCreate} className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-gray-700 mb-1">Campaign Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Q4 Client Update"
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-xs focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block font-semibold text-gray-700 mb-1">Subject (Supports Variables)</label>
                <input
                  type="text"
                  required
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-xs focus:outline-none focus:border-blue-500 font-mono"
                />
              </div>

              <div>
                <label className="block font-semibold text-gray-700 mb-1">HTML Body</label>
                <textarea
                  rows={4}
                  required
                  value={bodyHtml}
                  onChange={(e) => setBodyHtml(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-xs focus:outline-none focus:border-blue-500 font-mono"
                />
              </div>

              <div>
                <label className="block font-semibold text-gray-700 mb-1">Recipients (Format: email, first_name)</label>
                <textarea
                  rows={3}
                  required
                  value={recipientsText}
                  onChange={(e) => setRecipientsText(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-xs focus:outline-none focus:border-blue-500 font-mono"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 border border-gray-200 text-gray-600 rounded-lg text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-sm"
                >
                  Save Campaign
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
