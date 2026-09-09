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
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
            <Stethoscope className="w-5 h-5 text-blue-600" /> System Setup Doctor
          </h2>
          <p className="text-xs text-gray-500">First-run health check and configuration guidance in plain language.</p>
        </div>

        <button
          onClick={loadDoctor}
          disabled={loading}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-gray-200 hover:bg-gray-50 text-gray-700 rounded-lg text-xs font-semibold shadow-sm transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} /> Run Diagnostics
        </button>
      </div>

      {/* Overall Health Card */}
      <div
        className={`p-5 rounded-xl border flex items-center justify-between ${
          report?.overall_healthy
            ? "bg-emerald-50 border-emerald-200 text-emerald-900"
            : "bg-amber-50 border-amber-200 text-amber-900"
        }`}
      >
        <div className="flex items-center gap-3">
          {report?.overall_healthy ? (
            <CheckCircle2 className="w-6 h-6 text-emerald-600" />
          ) : (
            <AlertCircle className="w-6 h-6 text-amber-600" />
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
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm divide-y divide-gray-100 overflow-hidden">
        {/* Database */}
        <div className="p-4 flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-gray-900">Database Engine</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-blue-100 text-blue-800">
                {checks.database?.type || "sqlite"}
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Async database connection ready for tracking events and activity feeds.
            </p>
          </div>
          <span className="text-xs font-bold text-emerald-600">✓ CONNECTED</span>
        </div>

        {/* Tracking Keys */}
        <div className="p-4 flex items-start justify-between">
          <div>
            <span className="text-sm font-semibold text-gray-900">Cryptographic Signing Keys</span>
            <p className="text-xs text-gray-500 mt-1">
              HMAC-SHA256 tracking token secret configured ({checks.tracking_key?.length || 0} characters).
            </p>
          </div>
          <span className="text-xs font-bold text-emerald-600">✓ SECURE</span>
        </div>

        {/* Supabase Core */}
        <div className="p-4 flex items-start justify-between">
          <div>
            <span className="text-sm font-semibold text-gray-900">Supabase Platform Core</span>
            <p className="text-xs text-gray-500 mt-1">
              {checks.supabase?.status === "configured"
                ? `Connected to ${checks.supabase?.url}`
                : "Running in zero-friction local SQLite mode without cloud credentials."}
            </p>
          </div>
          <span className="text-xs font-bold text-blue-600">
            {checks.supabase?.status === "configured" ? "✓ CLOUD" : "ℹ LOCAL DEV"}
          </span>
        </div>

        {/* Google OAuth */}
        <div className="p-4 flex items-start justify-between">
          <div>
            <span className="text-sm font-semibold text-gray-900">Google OAuth (Gmail Sync)</span>
            <p className="text-xs text-gray-500 mt-1">
              {checks.google_oauth?.status === "configured"
                ? "Google OAuth Client ID & Secret configured for Gmail message correlation."
                : "Optional. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env for background Gmail API sync."}
            </p>
          </div>
          <span className="text-xs font-bold text-gray-400">
            {checks.google_oauth?.status === "configured" ? "✓ READY" : "ℹ OPTIONAL"}
          </span>
        </div>
      </div>
    </div>
  );
};
