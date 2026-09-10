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
} from "lucide-react";

interface NavProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onLogout?: () => void;
}

export const Navigation: React.FC<NavProps> = ({ activeTab, setActiveTab, onLogout }) => {
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
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col justify-between h-screen fixed left-0 top-0 select-none">
      <div>
        {/* Brand Header */}
        <div className="h-16 flex items-center px-6 border-b border-gray-100 gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-sm shadow-sm">
            ✓✓
          </div>
          <div>
            <h1 className="font-semibold text-gray-900 text-sm tracking-tight">Personal Mailtrack</h1>
            <p className="text-[11px] text-gray-400 font-medium">Free-Tier Email Suite</p>
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
                    ? "bg-blue-50 text-blue-700 font-semibold"
                    : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-blue-600" : "text-gray-400"}`} />
                {item.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer Actions */}
      <div className="p-4 border-t border-gray-100 space-y-2">
        <a
          href="https://mail.google.com"
          target="_blank"
          rel="noreferrer"
          className="flex items-center justify-between w-full px-3 py-2 bg-gray-50 hover:bg-gray-100 rounded-lg text-xs font-medium text-gray-700 transition"
        >
          <span>Open Gmail in Brave</span>
          <ExternalLink className="w-3.5 h-3.5 text-gray-400" />
        </a>

        {onLogout && (
          <button
            onClick={onLogout}
            className="flex items-center justify-between w-full px-3 py-2 text-xs font-medium text-red-600 hover:bg-red-50 rounded-lg transition"
          >
            <span>Sign Out</span>
            <LogOut className="w-3.5 h-3.5 text-red-400" />
          </button>
        )}
      </div>
    </aside>
  );
};
