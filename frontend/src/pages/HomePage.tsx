import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useResearchState, useResearch } from "../context/ResearchContext";
import SearchForm from "../components/SearchForm";
import ProgressStepper from "../components/ProgressStepper";

function HomeContent() {
  const { phase, sessionId } = useResearchState();
  const navigate = useNavigate();

  useEffect(() => {
    if (phase === "done" && sessionId) {
      navigate(`/research/${sessionId}`);
    }
  }, [phase, sessionId, navigate]);

  if (phase === "idle" || phase === "running" || phase === "error") {
    return (
      <>
        <SearchForm />
        <ProgressStepper />
      </>
    );
  }

  return null;
}

export default function HomePage() {
  const [, dispatch] = useResearch();

  useEffect(() => {
    dispatch({ type: "RESET" });
  }, [dispatch]);

  return (
    <>
      <div className="mx-auto max-w-4xl px-4 md:px-6 py-8">
        <header className="mb-8">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Research Agent</h1>
              <p className="text-sm text-gray-500">
                AI-powered research with citation-grounded factual reporting
              </p>
            </div>
          </div>
        </header>
        <main>
          <HomeContent />
        </main>
      </div>
    </>
  );
}
