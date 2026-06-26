import { useState, type FormEvent } from "react";
import { useResearch, chainSSEToDispatch } from "../context/ResearchContext";
import { connectResearchSSE } from "../api/sse";

export default function SearchForm() {
  const [query, setQuery] = useState("");
  const [state, dispatch] = useResearch();
  const disabled = state.phase === "running";

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!query.trim() || disabled) return;

    const res = await fetch("/api/research", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: query.trim() }),
    });
    const { session_id } = await res.json();

    dispatch({ type: "START", query: query.trim(), sessionId: session_id });
    setQuery("");
    connectResearchSSE(session_id, chainSSEToDispatch(dispatch));
  }

  return (
    <form onSubmit={handleSubmit} className="mb-6">
      <div className="flex flex-col gap-2 md:flex-row">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter a research topic..."
          disabled={disabled}
          className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200 disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={disabled || !query.trim()}
          className="rounded-lg bg-blue-600 px-6 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 md:w-auto w-full"
        >
          {disabled ? "Running..." : "Research"}
        </button>
      </div>
    </form>
  );
}
