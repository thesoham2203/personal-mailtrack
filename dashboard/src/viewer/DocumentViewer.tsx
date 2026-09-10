/**
 * Hosted Document & PDF Viewer with Buffered Session Beacon.
 * (PRD Section 43 & Requirement 26)
 */

import React, { useEffect, useState, useRef } from "react";
import { Download, ShieldCheck, Clock } from "lucide-react";
import { API_BASE } from "../services/api";

interface DocMetadata {
  title: string;
  total_pages: number;
  download_allowed: boolean;
  watermark?: string;
  recipient_email?: string;
}

export const DocumentViewer: React.FC<{ shareToken: string }> = ({ shareToken }) => {
  const [meta, setMeta] = useState<DocMetadata | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageTimes, setPageTimes] = useState<Record<number, number>>({});
  const [error, setError] = useState<string | null>(null);

  const activePageRef = useRef(1);
  const pageStartTimeRef = useRef(Date.now());
  const bufferRef = useRef<{ page_number: number; duration_seconds: number }[]>([]);

  // Flush buffered events to backend
  const flushBuffer = () => {
    if (bufferRef.current.length === 0) return;
    const payload = { events: [...bufferRef.current] };
    bufferRef.current = [];

    const url = `${API_BASE}/d/${shareToken}/event`;
    if (navigator.sendBeacon) {
      navigator.sendBeacon(url, new Blob([JSON.stringify(payload)], { type: "application/json" }));
    } else {
      fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        keepalive: true,
      }).catch(() => {});
    }
  };

  const recordCurrentPageDuration = () => {
    const durationSec = (Date.now() - pageStartTimeRef.current) / 1000.0;
    if (durationSec > 0.5) {
      const pageNum = activePageRef.current;
      bufferRef.current.push({
        page_number: pageNum,
        duration_seconds: Math.round(durationSec * 10) / 10,
      });
      setPageTimes((prev) => ({
        ...prev,
        [pageNum]: (prev[pageNum] || 0) + Math.round(durationSec),
      }));
    }
    pageStartTimeRef.current = Date.now();
  };

  useEffect(() => {
    // 1. Fetch document metadata
    fetch(`${API_BASE}/d/${shareToken}`)
      .then(async (res) => {
        if (!res.ok) throw new Error("Document link expired or invalid.");
        return res.json();
      })
      .then(setMeta)
      .catch((err) => setError(err.message));

    // 2. Periodic buffer flush every 15s
    const interval = setInterval(() => {
      recordCurrentPageDuration();
      flushBuffer();
    }, 15000);

    // 3. Flush on visibility hidden or unload
    const handleVisibilityChange = () => {
      if (document.visibilityState === "hidden") {
        recordCurrentPageDuration();
        flushBuffer();
      }
    };
    window.addEventListener("visibilitychange", handleVisibilityChange);
    window.addEventListener("beforeunload", () => {
      recordCurrentPageDuration();
      flushBuffer();
    });

    return () => {
      clearInterval(interval);
      window.removeEventListener("visibilitychange", handleVisibilityChange);
      recordCurrentPageDuration();
      flushBuffer();
    };
  }, [shareToken]);

  const switchPage = (nextPage: number) => {
    recordCurrentPageDuration();
    activePageRef.current = nextPage;
    setCurrentPage(nextPage);
  };

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white p-8 rounded-2xl border border-gray-200 shadow-sm text-center max-w-sm">
          <div className="w-12 h-12 rounded-full bg-red-100 text-red-600 flex items-center justify-center mx-auto mb-4 font-bold text-xl">
            ✕
          </div>
          <h2 className="text-base font-bold text-gray-900 mb-1">Access Restricted</h2>
          <p className="text-xs text-gray-500">{error}</p>
        </div>
      </div>
    );
  }

  if (!meta) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-sm text-gray-400 font-medium">Loading document viewer...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col justify-between">
      {/* Viewer Header */}
      <header className="h-14 bg-gray-800 border-b border-gray-700 px-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <ShieldCheck className="w-5 h-5 text-blue-400" />
          <h1 className="text-sm font-semibold truncate">{meta.title}</h1>
        </div>

        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1.5 bg-gray-700 px-3 py-1.5 rounded-lg">
            <Clock className="w-3.5 h-3.5 text-gray-400" />
            <span>Dwell: {pageTimes[currentPage] || 0}s</span>
          </div>

          {meta.download_allowed && (
            <button
              onClick={() => alert("Downloading original verified document...")}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition"
            >
              <Download className="w-3.5 h-3.5" /> Download
            </button>
          )}
        </div>
      </header>

      {/* Main Document Body with Watermark */}
      <main className="flex-1 flex items-center justify-center p-8 relative overflow-hidden select-none">
        <div className="bg-white text-gray-900 w-full max-w-2xl min-h-[600px] rounded-xl shadow-2xl p-12 relative flex flex-col justify-between border border-gray-300">
          {/* Dynamic Watermark */}
          {meta.watermark && (
            <div className="absolute inset-0 pointer-events-none flex items-center justify-center rotate-[-30deg] opacity-15 text-2xl font-bold text-gray-600 uppercase tracking-widest text-center px-4">
              {meta.watermark}
            </div>
          )}

          <div>
            <div className="border-b border-gray-100 pb-4 mb-6">
              <h2 className="text-xl font-bold text-gray-900">{meta.title}</h2>
              <p className="text-xs text-gray-400 mt-1">
                Confidential Page {currentPage} of {meta.total_pages}
              </p>
            </div>

            <div className="space-y-4 text-sm text-gray-700 leading-relaxed">
              <p>
                This document is securely tracked. Reading duration and page completion analytics are recorded
                to provide interaction insights.
              </p>
              <div className="p-4 bg-gray-50 rounded-lg border border-gray-200 text-xs font-mono text-gray-600">
                Sample Content Page {currentPage}: Executive overview, strategic milestones, and delivery specifications.
              </div>
            </div>
          </div>

          <div className="border-t border-gray-100 pt-4 flex justify-between items-center text-xs text-gray-400">
            <span>Verified Document Preview</span>
            <span>Page {currentPage} of {meta.total_pages}</span>
          </div>
        </div>
      </main>

      {/* Pagination Footer */}
      <footer className="h-14 bg-gray-800 border-t border-gray-700 px-6 flex items-center justify-center gap-4 text-xs font-medium">
        <button
          onClick={() => switchPage(Math.max(1, currentPage - 1))}
          disabled={currentPage <= 1}
          className="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 disabled:opacity-40 rounded-lg transition"
        >
          Previous
        </button>

        <span className="font-mono">
          {currentPage} / {meta.total_pages}
        </span>

        <button
          onClick={() => switchPage(Math.min(meta.total_pages, currentPage + 1))}
          disabled={currentPage >= meta.total_pages}
          className="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 disabled:opacity-40 rounded-lg transition"
        >
          Next
        </button>
      </footer>
    </div>
  );
};
