import {
  createContext,
  useContext,
  useReducer,
  type ReactNode,
} from "react";
import type { SSEEvent } from "../api/sse";

interface ResearchState {
  phase: "idle" | "running" | "done" | "error";
  currentNode: string | null;
  warnings: string[];
  errorMessage: string | null;
  sessionId: string | null;
  currentQuery: string | null;
}

type ResearchAction =
  | { type: "START"; query: string; sessionId: string }
  | { type: "STATUS"; node: string }
  | { type: "WARNING"; message: string }
  | { type: "DONE" }
  | { type: "ERROR"; message: string }
  | { type: "RESET" };

function researchReducer(
  state: ResearchState,
  action: ResearchAction,
): ResearchState {
  switch (action.type) {
    case "RESET":
      return { ...initialState };
    case "START":
      return {
        phase: "running",
        currentNode: null,
        warnings: [],
        errorMessage: null,
        sessionId: action.sessionId,
        currentQuery: action.query,
      };
    case "STATUS":
      return { ...state, currentNode: action.node };
    case "WARNING":
      return {
        ...state,
        warnings: [...state.warnings, action.message],
      };
    case "DONE":
      return { ...state, phase: "done" };
    case "ERROR":
      return { ...state, phase: "error", errorMessage: action.message };
    default:
      return state;
  }
}

const initialState: ResearchState = {
  phase: "idle",
  currentNode: null,
  warnings: [],
  errorMessage: null,
  sessionId: null,
  currentQuery: null,
};

function useResearchReducer() {
  return useReducer(researchReducer, initialState);
}

const ResearchContext = createContext<ReturnType<typeof useResearchReducer> | null>(null);

export function ResearchProvider({ children }: { children: ReactNode }) {
  const value = useResearchReducer();
  return (
    <ResearchContext.Provider value={value}>
      {children}
    </ResearchContext.Provider>
  );
}

export function useResearch() {
  const ctx = useContext(ResearchContext);
  if (!ctx) throw new Error("useResearch must be used within ResearchProvider");
  return ctx;
}

export function useResearchState() {
  const [state] = useResearch();
  return state;
}

export function chainSSEToDispatch(
  dispatch: React.Dispatch<ResearchAction>,
) {
  return (event: SSEEvent) => {
    switch (event.event) {
      case "status":
        dispatch({ type: "STATUS", node: event.data.node });
        break;
      case "warning":
        dispatch({ type: "WARNING", message: event.data.message });
        break;
      case "done":
        dispatch({ type: "DONE" });
        break;
      case "research_error":
        dispatch({ type: "ERROR", message: event.data.message });
        break;
      case "error":
        dispatch({ type: "ERROR", message: event.data.message });
        break;
    }
  };
}
