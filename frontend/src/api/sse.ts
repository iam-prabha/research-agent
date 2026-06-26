import { API_BASE } from "./api";

export type SSEEvent =
  | { event: "status"; data: { node: string } }
  | { event: "warning"; data: { message: string } }
  | { event: "progress"; data: { node: string; current: number; total: number } }
  | { event: "done"; data: { report: string } }
  | { event: "research_error"; data: { message: string } }
  | { event: "error"; data: { message: string } };

type EventCallback = (event: SSEEvent) => void;

export function connectResearchSSE(
  sessionId: string,
  onEvent: EventCallback,
  onError?: (err: Error) => void,
): () => void {
  const url = `${API_BASE}/api/research/${sessionId}/stream`;
  const source = new EventSource(url);
  let settled = false;

  function settle(event: SSEEvent) {
    if (settled) return;
    settled = true;
    onEvent(event);
    source.close();
  }

  source.addEventListener("status", (e) => {
    onEvent({ event: "status", data: JSON.parse(e.data) });
  });

  source.addEventListener("warning", (e) => {
    onEvent({ event: "warning", data: JSON.parse(e.data) });
  });

  source.addEventListener("progress", (e) => {
    onEvent({ event: "progress", data: JSON.parse(e.data) });
  });

  source.addEventListener("done", (e) => {
    settle({ event: "done", data: JSON.parse(e.data) });
  });

  source.addEventListener("research_error", (e) => {
    settle({ event: "research_error", data: JSON.parse(e.data) });
  });

  source.addEventListener("error", () => {
    settle({ event: "research_error", data: { message: "Connection lost — server may be unreachable" } });
    onError?.(new Error("SSE connection error"));
  });

  return () => source.close();
}
