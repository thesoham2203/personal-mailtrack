import React, { useEffect, useState } from "react";
import { fetchTemplates, createTemplate } from "../services/api";
import { Plus, Bookmark, Copy, Check } from "lucide-react";

export const TemplatesPage: React.FC = () => {
  const [templates, setTemplates] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [title, setTitle] = useState("");
  const [subject, setSubject] = useState("");
  const [bodyHtml, setBodyHtml] = useState("");
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const loadTemplates = async () => {
    try {
      const data = await fetchTemplates();
      setTemplates(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTemplates();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createTemplate({ title, subject, body_html: bodyHtml });
      setShowModal(false);
      setTitle("");
      setSubject("");
      setBodyHtml("");
      loadTemplates();
    } catch (err) {
      alert("Failed to create template.");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-lg font-bold text-gray-900">Email Templates</h2>
          <p className="text-xs text-gray-500">Create reusable snippets and full emails with dynamic merge tags.</p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-sm transition"
        >
          <Plus className="w-4 h-4" /> New Template
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {loading ? (
          <div className="col-span-2 p-8 text-center text-sm text-gray-400">Loading templates...</div>
        ) : templates.length === 0 ? (
          <div className="col-span-2 p-8 text-center text-sm text-gray-400">No templates yet. Create your first template!</div>
        ) : (
          templates.map((t) => (
            <div key={t.id} className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm space-y-3">
              <div className="flex justify-between items-start">
                <div className="flex items-center gap-2">
                  <Bookmark className="w-4 h-4 text-blue-600" />
                  <h3 className="text-sm font-semibold text-gray-900">{t.title}</h3>
                </div>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(t.body_html);
                    setCopiedId(t.id);
                    setTimeout(() => setCopiedId(null), 2000);
                  }}
                  className="text-xs text-gray-400 hover:text-blue-600 flex items-center gap-1"
                >
                  {copiedId === t.id ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                  {copiedId === t.id ? "Copied" : "Copy"}
                </button>
              </div>

              <div className="text-xs text-gray-600 font-medium">Subject: {t.subject}</div>
              <div
                className="text-xs text-gray-500 bg-gray-50 p-3 rounded-lg border border-gray-100 font-mono line-clamp-3"
                dangerouslySetInnerHTML={{ __html: t.body_html }}
              />
            </div>
          ))
        )}
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full border border-gray-200 shadow-xl p-6">
            <h3 className="text-base font-bold text-gray-900 mb-4">Create Template</h3>
            <form onSubmit={handleCreate} className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-gray-700 mb-1">Title</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Follow-up after meeting"
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-xs focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block font-semibold text-gray-700 mb-1">Subject</label>
                <input
                  type="text"
                  required
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  placeholder="e.g. Great speaking with you, {{first_name}}"
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-xs focus:outline-none focus:border-blue-500 font-mono"
                />
              </div>

              <div>
                <label className="block font-semibold text-gray-700 mb-1">Body HTML</label>
                <textarea
                  rows={4}
                  required
                  value={bodyHtml}
                  onChange={(e) => setBodyHtml(e.target.value)}
                  placeholder="<p>Hi {{first_name}},</p><p>Thanks for your time today...</p>"
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
                  Save Template
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
