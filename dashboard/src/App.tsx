import React, { useState } from "react";
import { ThemeProvider } from "./context/ThemeContext";
import { Navigation } from "./components/Navigation";
import { ActivityPage } from "./pages/ActivityPage";
import { EmailsPage } from "./pages/EmailsPage";
import { FollowUpPage } from "./pages/FollowUpPage";
import { ContactsPage } from "./pages/ContactsPage";
import { CampaignsPage } from "./pages/CampaignsPage";
import { DocumentsPage } from "./pages/DocumentsPage";
import { TemplatesPage } from "./pages/TemplatesPage";
import { ReportsPage } from "./pages/ReportsPage";
import { SetupDoctorPage } from "./pages/SetupDoctorPage";
import { DocumentViewer } from "./viewer/DocumentViewer";
import { LoginPage } from "./pages/LoginPage";
import { isAuthenticated, logout } from "./services/auth";

const AppContent: React.FC = () => {
  const [isAuthed, setIsAuthed] = useState<boolean>(() => isAuthenticated());
  const [activeTab, setActiveTab] = useState<string>("activity");

  // Check if current route is public document viewer: /d/{share_token}
  const path = window.location.pathname;
  if (path.startsWith("/d/")) {
    const shareToken = path.replace("/d/", "").split("/")[0];
    return <DocumentViewer shareToken={shareToken} />;
  }

  if (!isAuthed) {
    return <LoginPage onLoginSuccess={() => setIsAuthed(true)} />;
  }

  const handleLogout = () => {
    logout();
    setIsAuthed(false);
  };

  const renderActivePage = () => {
    switch (activeTab) {
      case "activity":
        return <ActivityPage />;
      case "emails":
        return <EmailsPage />;
      case "followup":
        return <FollowUpPage />;
      case "contacts":
        return <ContactsPage />;
      case "campaigns":
        return <CampaignsPage />;
      case "documents":
        return <DocumentsPage />;
      case "templates":
        return <TemplatesPage />;
      case "reports":
        return <ReportsPage />;
      case "doctor":
        return <SetupDoctorPage />;
      default:
        return <ActivityPage />;
    }
  };

  return (
    <div className="flex min-h-screen bg-[#f8fafd] dark:bg-slate-950 text-gray-900 dark:text-slate-100 transition-colors duration-200">
      <Navigation activeTab={activeTab} setActiveTab={setActiveTab} onLogout={handleLogout} />
      <main className="flex-1 ml-64 p-8 max-w-6xl">
        {renderActivePage()}
      </main>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
};
