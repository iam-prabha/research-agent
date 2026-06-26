import { useResearchState } from "../context/ResearchContext";

const NODES = ["plan", "search", "extract", "synthesize", "verify"];

const LABELS: Record<string, string> = {
  plan: "Planning",
  search: "Searching",
  extract: "Extracting",
  synthesize: "Synthesizing",
  verify: "Verifying",
};

export default function ProgressStepper() {
  const { phase, currentNode, warnings } = useResearchState();

  if (phase === "idle") return null;

  const currentIdx = currentNode ? NODES.indexOf(currentNode) : -1;

  return (
    <div className="mb-6">
      {/* Desktop: horizontal row */}
      <div className="hidden md:block">
        <div className="flex items-center justify-between">
          {NODES.map((node, i) => {
            const isActive = node === currentNode;
            const isDone = currentIdx > i;
            const isPending = currentIdx < i;
            return (
              <div key={node} className="flex flex-col items-center">
                <div
                  className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold
                    ${isDone ? "bg-green-500 text-white" : ""}
                    ${isActive ? "bg-blue-600 text-white ring-2 ring-blue-300" : ""}
                    ${isPending ? "bg-gray-200 text-gray-500" : ""}
                  `}
                >
                  {isDone ? "✓" : i + 1}
                </div>
                <span
                  className={`mt-1 text-xs ${
                    isActive ? "font-semibold text-blue-600" : "text-gray-500"
                  }`}
                >
                  {LABELS[node]}
                </span>
              </div>
            );
          })}
        </div>

        {phase === "running" && (
          <div className="mt-4 h-2 w-full overflow-hidden rounded-full bg-gray-200">
            <div
              className="h-full rounded-full bg-blue-600 transition-all duration-500"
              style={{
                width: `${((currentIdx + 1) / NODES.length) * 100}%`,
              }}
            />
          </div>
        )}
      </div>

      {/* Mobile: vertical list */}
      <div className="md:hidden">
        {NODES.map((node, i) => {
          const isActive = node === currentNode;
          const isDone = currentIdx > i;
          const isPending = currentIdx < i;
          return (
            <div key={node} className="flex items-center gap-3 py-2">
              <div
                className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-bold
                  ${isDone ? "bg-green-500 text-white" : ""}
                  ${isActive ? "bg-blue-600 text-white ring-2 ring-blue-300" : ""}
                  ${isPending ? "bg-gray-200 text-gray-500" : ""}
                `}
              >
                {isDone ? "✓" : i + 1}
              </div>
              <span
                className={`text-sm ${
                  isActive ? "font-semibold text-blue-600" : "text-gray-500"
                }`}
              >
                {LABELS[node]}
              </span>
              {i < NODES.length - 1 && (
                <div
                  className={`ml-[10px] w-0.5 self-stretch ${
                    isDone ? "bg-green-500" : "bg-gray-200"
                  }`}
                />
              )}
            </div>
          );
        })}

        {phase === "running" && (
          <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-gray-200">
            <div
              className="h-full rounded-full bg-blue-600 transition-all duration-500"
              style={{
                width: `${((currentIdx + 1) / NODES.length) * 100}%`,
              }}
            />
          </div>
        )}
      </div>

      {warnings.length > 0 && (
        <div className="mt-3 rounded-lg border border-yellow-300 bg-yellow-50 px-3 py-2 text-xs text-yellow-800">
          {warnings.map((w, i) => (
            <p key={i}>⚠ {w}</p>
          ))}
        </div>
      )}
    </div>
  );
}
