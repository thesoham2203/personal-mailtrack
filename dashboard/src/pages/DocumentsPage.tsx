import React, { useEffect, useState } from "react";
import { fetchDocuments, uploadDocument, createDocumentShare, fetchDocumentAnalytics } from "../services/api";
import { Upload, Share2, BarChart2, Eye, Copy, Check } from "lucide-react";

export const DocumentsPage: React.FC = () => {
  const [docs, setDocs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [selectedAnalytics, setSelectedAnalytics] = useState<any>(null);
  const [createdShareUrl, setCreatedShareUrl] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const loadDocs = async () => {
    try {
      const data = await fetchDocuments();
      setDocs(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocs();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      await uploadDocument(file, file.name.replace(".pdf", ""));
      await loadDocs();
    } catch (err) {
      alert("Failed to upload document.");
    } finally {
      setUploading(false);
    }
  };

  const handleCreateShare = async (docId: string) => {
    const recipient = prompt("Enter recipient email (optional, for watermarking & tracking):");
    try {
      const res = await createDocumentShare(docId, {
        recipient_email: recipient || undefined,
        watermark_text: recipient ? `CONFIDENTIAL - ${recipient}` : undefined,
      });
      setCreatedShareUrl(res.viewer_url);
    } catch (err) {
      alert("Failed to create share link.");
    }
  };

  const handleViewAnalytics = async (docId: string) => {
    try {
      const data = await fetchDocumentAnalytics(docId);
      setSelectedAnalytics(data);
    } catch (err) {
      alert("Could not load document analytics.");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-lg font-bold text-gray-900">Tracked Documents & PDFs</h2>
          <p className="text-xs text-gray-500">Securely share documents and view page-by-page reader duration analytics.</p>
        </div>

        <label className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-sm cursor-pointer transition">
          <Upload className="w-4 h-4" />
          <span>{uploading ? "Uploading..." : "Upload Tracked PDF"}</span>
          <input type="file" accept="application/pdf" onChange={handleFileUpload} className="hidden" />
        </label>
      </div>

      {/* Share URL Banner */}
      {createdShareUrl && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center justify-between text-xs text-emerald-800">
          <div>
            <span className="font-semibold">Tracked Share Link Ready: </span>
            <span className="font-mono">{createdShareUrl}</span>
          </div>
          <button
            onClick={() => {
              navigator.clipboard.writeText(createdShareUrl);
              setCopied(true);
              setTimeout(() => setCopied(false), 2000);
            }}
            className="flex items-center gap-1.5 px-3 py-1 bg-emerald-600 text-white rounded-lg font-semibold"
          >
            {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
            {copied ? "Copied" : "Copy Link"}
          </button>
        </div>
      )}

      {/* Documents List */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden divide-y divide-gray-100">
        {loading ? (
          <div className="p-8 text-center text-sm text-gray-400">Loading documents...</div>
        ) : docs.length === 0 ? (
          <div className="p-8 text-center text-sm text-gray-400">No documents uploaded yet. Upload a PDF above!</div>
        ) : (
          docs.map((d) => (
            <div key={d.id} className="p-4 flex items-center justify-between hover:bg-gray-50 transition">
              <div>
                <h3 className="text-sm font-semibold text-gray-900">{d.title}</h3>
                <div className="text-xs text-gray-500 mt-0.5">
                  {d.filename} · {Math.round(d.file_size_bytes / 1024)} KB · {d.shares_count} active shares
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleCreateShare(d.id)}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 text-blue-700 hover:bg-blue-100 rounded-lg text-xs font-medium transition"
                >
                  <Share2 className="w-3.5 h-3.5" /> Share Link
                </button>
                <button
                  onClick={() => handleViewAnalytics(d.id)}
                  className="flex items-center gap-1.5 px-3 py-1.5 border border-gray-200 text-gray-700 hover:bg-gray-50 rounded-lg text-xs font-medium transition"
                >
                  <BarChart2 className="w-3.5 h-3.5" /> Analytics
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Analytics Modal */}
      {selectedAnalytics && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full border border-gray-200 shadow-xl p-6">
            <h3 className="text-base font-bold text-gray-900 mb-1">Document Page Analytics</h3>
            <p className="text-xs text-gray-500 mb-4">{selectedAnalytics.title}</p>

            <div className="space-y-3 text-xs">
              <div className="bg-gray-50 p-3 rounded-lg flex justify-between">
                <span>Total View Sessions:</span>
                <span className="font-bold text-gray-900">{selectedAnalytics.total_views}</span>
              </div>

              <div className="font-semibold text-gray-700">Page-by-Page Dwell Duration:</div>
              {selectedAnalytics.page_analytics.length === 0 ? (
                <div className="text-gray-400 italic">No readers have viewed pages yet.</div>
              ) : (
                <div className="space-y-2">
                  {selectedAnalytics.page_analytics.map((p: any) => (
                    <div key={p.page} className="flex justify-between items-center border border-gray-100 p-2 rounded">
                      <span className="font-medium">Page {p.page}</span>
                      <span className="font-mono text-blue-600 font-bold">{p.total_duration_seconds}s</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setSelectedAnalytics(null)}
                className="px-4 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-xs font-semibold"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
