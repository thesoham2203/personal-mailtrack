import React, { useEffect, useState } from "react";
import { fetchSummary } from "../services/api";
import { BarChart3, TrendingUp, Award, Download } from "lucide-react";

export const ReportsPage: React.FC = () => {
  const [summary, setSummary] = useState<any>(null);
  const [days, setDays] = useState(30);

  useEffect(() => {
    fetchSummary(days).then(setSummary);
  }, [days]);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-lg font-bold text-gray-900">Productivity & Analytics Reports</h2>
          <p className="text-xs text-gray-500">Summary metrics, response rates, and certified delivery evidence.</p>
        </div>

        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-xs font-semibold focus:outline-none"
        >
          <option value={7}>Last 7 Days</option>
          <option value={30}>Last 30 Days</option>
          <option value={90}>Last 90 Days</option>
        </select>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between text-gray-500 text-xs font-semibold">
            <span>TOTAL SENT</span>
            <TrendingUp className="w-4 h-4 text-blue-600" />
          </div>
          <div className="mt-3 text-3xl font-bold text-gray-900">{summary?.total_sent || 0}</div>
          <div className="mt-2 text-xs text-gray-400">Total recipients: {summary?.total_recipients || 0}</div>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between text-gray-500 text-xs font-semibold">
            <span>ENGAGEMENT RATE</span>
            <BarChart3 className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="mt-3 text-3xl font-bold text-emerald-600">{summary?.open_rate_percent || 0}%</div>
          <div className="mt-2 text-xs text-gray-400">Likely human opens: {summary?.total_human_opens || 0}</div>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between text-gray-500 text-xs font-semibold">
            <span>REPLY RATE</span>
            <TrendingUp className="w-4 h-4 text-purple-600" />
          </div>
          <div className="mt-3 text-3xl font-bold text-purple-600">{summary?.reply_rate_percent || 0}%</div>
          <div className="mt-2 text-xs text-gray-400">Total replies: {summary?.total_replies || 0}</div>
        </div>
      </div>

      {/* Export Section */}
      <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold text-gray-900 flex items-center gap-2">
            <Award className="w-4 h-4 text-blue-600" />
            Certified Delivery Evidence & Data Export
          </h3>
          <p className="text-xs text-gray-500 mt-0.5">
            Export a comprehensive JSON audit log of all emails, tracking timestamps, and cryptographic hashes.
          </p>
        </div>

        <button
          onClick={() => {
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(summary, null, 2));
            const downloadAnchor = document.createElement("a");
            downloadAnchor.setAttribute("href", dataStr);
            downloadAnchor.setAttribute("download", `mailtrack_summary_${days}d.json`);
            document.body.appendChild(downloadAnchor);
            downloadAnchor.click();
            downloadAnchor.remove();
          }}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-sm transition"
        >
          <Download className="w-4 h-4" /> Export Report Data
        </button>
      </div>
    </div>
  );
};
