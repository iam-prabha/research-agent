import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useResearchState } from "../context/ResearchContext";
import ConfirmDialog from "./ConfirmDialog";
import { API_BASE } from "../api/api";

interface Props {
  open: boolean;
  onToggle: () => void;
}

interface HistoryEntry {
  id: string;
  query: string;
  status: string;
  has_report: boolean;
  created_at: string | null;
}

export default function HistorySidebar({ open, onToggle }: Props) {
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const navigate = useNavigate();
  const { sessionId, phase } = useResearchState();

  const fetchHistory = useCallback(async () => {
    const res = await fetch(`${API_BASE}/api/research/history`);
    const data: HistoryEntry[] = await res.json();
    setHistory(data);
  }, []);

  useEffect(() => {
    fetchHistory();
  }, [sessionId, phase, fetchHistory]);

  useEffect(() => {
    if (open) fetchHistory();
  }, [open, fetchHistory]);

  async function deleteEntry(id: string) {
    setDeletingId(null);
    setHistory((prev) => prev.filter((e) => e.id !== id));
    if (sessionId === id) navigate("/");
    await fetch(`${API_BASE}/api/research/${id}`, { method: "DELETE" });
  }

  function loadSession(entry: HistoryEntry) {
    if (!entry.has_report) return;
    navigate(`/research/${entry.id}`);
    onToggle();
  }

  function formatTime(iso: string | null) {
    if (!iso) return "";
    const d = new Date(iso);
    return d.toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  function statusBadge(status: string) {
    const styles: Record<string, string> = {
      completed: "bg-green-100 text-green-700",
      failed: "bg-red-100 text-red-700",
    };
    return styles[status] ?? "bg-yellow-100 text-yellow-700";
  }

  return (
    <>
      <button
        onClick={onToggle}
        className="fixed left-4 top-4 z-30 hidden md:flex h-10 w-10 items-center justify-center rounded-lg bg-white shadow-md ring-1 ring-gray-200 hover:bg-gray-50"
        title="Research history"
      >
        <svg className="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      {open && (
        <div
          className="fixed inset-0 z-20 bg-black/20"
          onClick={onToggle}
        />
      )}

      <aside
        className={`fixed left-0 top-0 z-30 h-full w-[85vw] max-w-sm md:w-80 transform bg-white shadow-xl transition-transform duration-300 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between border-b px-4 py-3">
          <h2 className="font-semibold text-gray-900">Research History</h2>
          <button
            onClick={onToggle}
            className="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>

        <div className="overflow-y-auto p-3" style={{ height: "calc(100% - 52px)" }}>
          {history.length === 0 && (
            <p className="py-8 text-center text-sm text-gray-400">No research sessions yet</p>
          )}

          {history.map((entry) => {
            const clickable = entry.has_report;
            return (
              <div key={entry.id} className="relative mb-2">
                <button
                  onClick={() => loadSession(entry)}
                  disabled={!clickable}
                  className={`w-full rounded-lg border p-3 pr-10 text-left transition-colors ${
                    clickable
                      ? "hover:bg-gray-50 cursor-pointer"
                      : "cursor-default opacity-60"
                  }`}
                >
                  <p className="truncate text-sm font-medium text-gray-900">
                    {entry.query}
                  </p>
                  <div className="mt-1 flex items-center justify-between">
                    <span className="text-xs text-gray-400">
                      {formatTime(entry.created_at)}
                    </span>
                    <span className={`rounded px-2 py-0.5 text-xs font-medium ${statusBadge(entry.status)}`}>
                      {entry.has_report ? entry.status : "No report"}
                    </span>
                  </div>
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setDeletingId(entry.id);
                  }}
                  className="absolute right-2 top-1/2 -translate-y-1/2 flex h-7 w-7 items-center justify-center rounded hover:bg-red-50 text-gray-400 hover:text-red-600"
                  title="Delete session"
                >
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            );
          })}
        </div>
      </aside>

      <ConfirmDialog
        open={deletingId !== null}
        title="Delete session"
        message="Are you sure you want to delete this research session? This cannot be undone."
        confirmLabel="Delete"
        onConfirm={() => {
          if (deletingId) deleteEntry(deletingId);
        }}
        onCancel={() => setDeletingId(null)}
      />
    </>
  );
}
