import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ResearchProvider } from "./context/ResearchContext";
import AppLayout from "./components/AppLayout";
import HomePage from "./pages/HomePage";
import ReportPage from "./pages/ReportPage";

export default function App() {
  return (
    <BrowserRouter>
      <ResearchProvider>
        <AppLayout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/research/:sessionId" element={<ReportPage />} />
          </Routes>
        </AppLayout>
      </ResearchProvider>
    </BrowserRouter>
  );
}
