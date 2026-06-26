import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import Markdown from "react-markdown";


interface SessionData {
  id: string;
  query: string;
  status: string;
  report_markdown: string | null;
  created_at: string | null;
}

function useCopyButton(text: string) {
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!copied) return;
    const id = setTimeout(() => setCopied(false), 2000);
    return () => clearTimeout(id);
  }, [copied]);

  return {
    copied,
    copy: async () => {
      await navigator.clipboard.writeText(text);
      setCopied(true);
    },
  };
}

function downloadMarkdown(text: string, filename: string) {
  const blob = new Blob([text], { type: "text/markdown" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function sanitizeFilename(query: string) {
  return (
    query
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "")
      .slice(0, 60) || "research-report"
  );
}

function Toolbar({ text, query }: { text: string; query: string }) {
  const { copied, copy } = useCopyButton(text);

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={copy}
        className="rounded border px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-50"
      >
        {copied ? "Copied!" : "Copy"}
      </button>
      <button
        onClick={() =>
          downloadMarkdown(text, `${sanitizeFilename(query)}.md`)
        }
        className="rounded border px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-50"
      >
        Download
      </button>
    </div>
  );
}

export default function ReportPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const [session, setSession] = useState<SessionData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) return;
    setLoading(true);
    setError(null);
      fetch(`/api/research/${sessionId}`)
      .then((r) => {
        if (!r.ok) throw new Error("Session not found");
        return r.json();
      })
      .then((data: SessionData) => {
        setSession(data);
        setLoading(false);
      })
      .catch((e: Error) => {
        setError(e.message);
        setLoading(false);
      });
  }, [sessionId]);

  if (loading) {
    return (
      <div className="mx-auto max-w-4xl px-4 md:px-6 py-8">
        <div className="flex items-center justify-center p-12 text-gray-400">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600" />
        </div>
      </div>
    );
  }

  if (error || !session) {
    return (
      <div className="mx-auto max-w-4xl px-4 md:px-6 py-8">
        <div className="rounded-lg border border-red-300 bg-red-50 p-6 text-red-700">
          <h3 className="font-semibold">Not Found</h3>
          <p className="mt-1 text-sm">{error || "Session not found"}</p>
          <Link
            to="/"
            className="mt-3 inline-block rounded bg-red-200 px-4 py-1.5 text-sm font-medium hover:bg-red-300"
          >
            Back to Home
          </Link>
        </div>
      </div>
    );
  }

  if (!session.report_markdown) {
    return (
      <div className="mx-auto max-w-4xl px-4 md:px-6 py-8">
        <div className="flex items-center justify-center rounded-lg border-2 border-dashed p-12 text-gray-400">
          <div className="text-center">
            <p className="text-lg">No report available</p>
            <p className="mt-1 text-sm">
              This session did not produce a research report
            </p>
            <Link
              to="/"
              className="mt-4 inline-block rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
            >
              New Research
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="mx-auto max-w-4xl px-4 md:px-6 py-8">
        <header className="mb-6">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10" />
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-3">
                <Link
                  to="/"
                  className="text-sm text-blue-600 hover:text-blue-700"
                >
                  ← New Research
                </Link>
                <span className="text-xs text-gray-400">
                  {session.created_at
                    ? new Date(session.created_at).toLocaleDateString()
                    : ""}
                </span>
                <span className="rounded bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">
                  {session.status}
                </span>
              </div>
              <h1 className="mt-1 truncate text-xl font-bold text-gray-900">
                {session.query}
              </h1>
            </div>
          </div>
        </header>

        <main>
          <div className="rounded-lg border bg-white shadow-sm">
            <div className="flex flex-col gap-2 border-b px-4 py-3 md:flex-row md:items-center md:justify-between md:px-6">
              <h2 className="text-lg font-semibold text-gray-900">
                Research Report
              </h2>
              <Toolbar
                text={session.report_markdown}
                query={session.query}
              />
            </div>
            <div className="prose prose-sm max-w-none p-4 md:p-6">
              <Markdown>{session.report_markdown}</Markdown>
            </div>
          </div>
        </main>
      </div>
    </>
  );
}
