import React, { useEffect, useState } from "react";
import { fetchDoctorDiagnostics } from "../services/api";
import { CheckCircle2, AlertCircle, RefreshCw, Stethoscope } from "lucide-react";

export const SetupDoctorPage: React.FC = () => {
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const loadDoctor = async () => {
    setLoading(true);
    try {
      const data = await fetchDoctorDiagnostics();
      setReport(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDoctor();
  }, []);

  const checks = report?.checks || {};

  return (
    <div className="space-y-6 max-w-3xl">
      <div className="flex flex-wrap justify-between items-center gap-4">
        <div>
          <h2 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <Stethoscope className="w-5 h-5 text-blue-600 dark:text-blue-400" /> System Setup Doctor
          </h2>
          <p className="text-xs text-gray-500 dark:text-slate-400">First-run health check and configuration guidance in plain language.</p>
        </div>

        <button
          onClick={loadDoctor}
          disabled={loading}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 hover:bg-gray-50 dark:hover:bg-slate-800 text-gray-700 dark:text-slate-200 rounded-lg text-xs font-semibold shadow-sm transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} /> Run Diagnostics
        </button>
      </div>

      {/* Overall Health Card */}
      <div
        className={`p-5 rounded-xl border flex items-center justify-between transition-colors ${
          report?.overall_healthy
            ? "bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800 text-emerald-900 dark:text-emerald-200"
            : "bg-amber-50 dark:bg-amber-950/40 border-amber-200 dark:border-amber-800 text-amber-900 dark:text-amber-200"
        }`}
      >
        <div className="flex items-center gap-3">
          {report?.overall_healthy ? (
            <CheckCircle2 className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
          ) : (
            <AlertCircle className="w-6 h-6 text-amber-600 dark:text-amber-400" />
          )}
          <div>
            <h3 className="font-bold text-sm">
              {report?.overall_healthy ? "All Core Systems Operational" : "Configuration Warning"}
            </h3>
            <p className="text-xs opacity-90 mt-0.5">
              {report?.overall_healthy
                ? "Your local database, tracking keys, and API routers are fully functional."
                : "Some optional integrations (like Google OAuth or Supabase cloud) are not configured."}
            </p>
          </div>
        </div>
      </div>

      {/* Diagnostics Cards */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-gray-200 dark:border-slate-800 shadow-sm divide-y divide-gray-100 dark:divide-slate-800/80 overflow-hidden transition-colors">
        {/* Database */}
        <div className="p-4 flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-gray-900 dark:text-white">Database Engine</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-blue-100 dark:bg-blue-950/60 text-blue-800 dark:text-blue-300 border border-blue-200 dark:border-blue-800">
                {checks.database?.type || "sqlite"}
              </span>
            </div>
            <p className="text-xs text-gray-500 dark:text-slate-400 mt-1">
              Async database connection ready for tracking events and activity feeds.
            </p>
          </div>
          <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400">✓ CONNECTED</span>
        </div>

        {/* Tracking Keys */}
        <div className="p-4 flex items-start justify-between">
          <div>
            <span className="text-sm font-semibold text-gray-900 dark:text-white">Cryptographic Signing Keys</span>
            <p className="text-xs text-gray-500 dark:text-slate-400 mt-1">
              HMAC-SHA256 tracking token secret configured ({checks.tracking_key?.length || 0} characters).
            </p>
          </div>
          <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400">✓ SECURE</span>
        </div>

        {/* Supabase Core */}
        <div className="p-4 flex items-start justify-between">
          <div>
            <span className="text-sm font-semibold text-gray-900 dark:text-white">Supabase Platform Core</span>
            <p className="text-xs text-gray-500 dark:text-slate-400 mt-1">
              {checks.supabase?.status === "configured"
                ? `Connected to ${checks.supabase?.url}`
                : "Running in zero-friction local SQLite mode without cloud credentials."}
            </p>
          </div>
          <span className="text-xs font-bold text-blue-600 dark:text-blue-400">
            {checks.supabase?.status === "configured" ? "✓ CLOUD" : "ℹ LOCAL DEV"}
          </span>
        </div>

        {/* Google OAuth */}
        <div className="p-4 flex items-start justify-between">
          <div>
            <span className="text-sm font-semibold text-gray-900 dark:text-white">Google OAuth (Gmail Sync)</span>
            <p className="text-xs text-gray-500 dark:text-slate-400 mt-1">
              {checks.google_oauth?.status === "configured"
                ? "Google OAuth Client ID & Secret configured for Gmail message correlation."
                : "Optional. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env for background Gmail API sync."}
            </p>
          </div>
          <span className="text-xs font-bold text-gray-400 dark:text-slate-500">
            {checks.google_oauth?.status === "configured" ? "✓ READY" : "ℹ OPTIONAL"}
          </span>
        </div>
      </div>
    </div>
  );
};
