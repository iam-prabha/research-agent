import { useState, type ReactNode } from "react";
import HistorySidebar from "./HistorySidebar";

interface Props {
  children: ReactNode;
}

export default function AppLayout({ children }: Props) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <>
      {/* Mobile nav bar */}
      <nav className="fixed top-0 left-0 right-0 z-30 flex h-12 items-center gap-3 border-b bg-white px-4 md:hidden">
        <button
          onClick={() => setSidebarOpen(true)}
          className="flex h-9 w-9 items-center justify-center rounded-lg hover:bg-gray-100"
          title="Research history"
        >
          <svg className="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <span className="font-semibold text-gray-900">Research Agent</span>
      </nav>

      {/* Page content */}
      <div className="md:pt-0 pt-12">
        <HistorySidebar
          open={sidebarOpen}
          onToggle={() => setSidebarOpen((v) => !v)}
        />
        {children}
      </div>
    </>
  );
}
