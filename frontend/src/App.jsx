import { Route, Routes } from "react-router";
import Header from "./components/Header.jsx";
import HistoryPage from "./pages/HistoryPage.jsx";
import QuizPage from "./pages/QuizPage.jsx";
import ResultsPage from "./pages/ResultsPage.jsx";
import UploadPage from "./pages/UploadPage.jsx";
import WorkspacePage from "./pages/WorkspacePage.jsx";

export default function App() {
  return (
    <div className="min-h-screen">
      <Header />
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/workspace/:documentId" element={<WorkspacePage />} />
        <Route path="/quiz/:quizId" element={<QuizPage />} />
        <Route path="/results/:quizId" element={<ResultsPage />} />
        <Route path="/history" element={<HistoryPage />} />
      </Routes>
    </div>
  );
}
