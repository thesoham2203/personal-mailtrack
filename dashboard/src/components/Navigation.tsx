import React from "react";
import {
  Activity,
  Mail,
  Clock,
  Users,
  Send,
  FileText,
  Bookmark,
  BarChart3,
  Stethoscope,
  ExternalLink,
  LogOut,
  Sun,
  Moon,
} from "lucide-react";
import { useTheme } from "../context/ThemeContext";

interface NavProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onLogout?: () => void;
}

export const Navigation: React.FC<NavProps> = ({ activeTab, setActiveTab, onLogout }) => {
  const { isDark, toggleTheme } = useTheme();

  const navItems = [
    { id: "activity", label: "Live Activity", icon: Activity },
    { id: "emails", label: "Tracked Emails", icon: Mail },
    { id: "followup", label: "Follow-Up Inbox", icon: Clock },
    { id: "contacts", label: "Contacts CRM", icon: Users },
    { id: "campaigns", label: "Campaigns", icon: Send },
    { id: "documents", label: "PDFs & Docs", icon: FileText },
    { id: "templates", label: "Templates", icon: Bookmark },
    { id: "reports", label: "Reports & Evidence", icon: BarChart3 },
    { id: "doctor", label: "Setup Doctor", icon: Stethoscope },
  ];

  return (
    <aside className="w-64 bg-white dark:bg-slate-900 border-r border-gray-200 dark:border-slate-800 flex flex-col justify-between h-screen fixed left-0 top-0 select-none transition-colors duration-200 z-20">
      <div>
        {/* Brand Header */}
        <div className="h-16 flex items-center px-6 border-b border-gray-100 dark:border-slate-800 gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-sm shadow-sm">
            ✓✓
          </div>
          <div>
            <h1 className="font-semibold text-gray-900 dark:text-white text-sm tracking-tight">Personal Mailtrack</h1>
            <p className="text-[11px] text-gray-400 dark:text-slate-400 font-medium">Free-Tier Email Suite</p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-400 font-semibold border-l-2 border-blue-600 dark:border-blue-500 -ml-[2px]"
                    : "text-gray-600 dark:text-slate-400 hover:bg-gray-50 dark:hover:bg-slate-800 hover:text-gray-900 dark:hover:text-slate-200"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-blue-600 dark:text-blue-400" : "text-gray-400 dark:text-slate-500"}`} />
                {item.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer Actions */}
      <div className="p-4 border-t border-gray-100 dark:border-slate-800 space-y-2">
        {/* Dark Mode Toggle */}
        <button
          onClick={toggleTheme}
          aria-label="Toggle dark mode"
          className="flex items-center justify-between w-full px-3 py-2 bg-gray-50 dark:bg-slate-800/80 hover:bg-gray-100 dark:hover:bg-slate-700/80 rounded-lg text-xs font-medium text-gray-700 dark:text-slate-200 transition border border-transparent dark:border-slate-700/50"
        >
          <span className="flex items-center gap-2">
            {isDark ? <Sun className="w-3.5 h-3.5 text-amber-400" /> : <Moon className="w-3.5 h-3.5 text-indigo-500" />}
            {isDark ? "Light Mode" : "Dark Mode"}
          </span>
          <span className="text-[10px] uppercase font-semibold text-gray-400 dark:text-slate-400">
            {isDark ? "ON" : "OFF"}
          </span>
        </button>

        <a
          href="https://mail.google.com"
          target="_blank"
          rel="noreferrer"
          className="flex items-center justify-between w-full px-3 py-2 bg-gray-50 dark:bg-slate-800/80 hover:bg-gray-100 dark:hover:bg-slate-700/80 rounded-lg text-xs font-medium text-gray-700 dark:text-slate-200 transition border border-transparent dark:border-slate-700/50"
        >
          <span>Open Gmail in Brave</span>
          <ExternalLink className="w-3.5 h-3.5 text-gray-400 dark:text-slate-400" />
        </a>

        {onLogout && (
          <button
            onClick={onLogout}
            className="flex items-center justify-between w-full px-3 py-2 text-xs font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/40 rounded-lg transition"
          >
            <span>Sign Out</span>
            <LogOut className="w-3.5 h-3.5 text-red-400" />
          </button>
        )}
      </div>
    </aside>
  );
};
