import { BrowserRouter, Routes, Route } from "react-router-dom";
import RunsPage from "./pages/RunsPage";
import RunDetailPage from "./pages/RunDetailPage";
import "./App.css";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<RunsPage />} />
        <Route path="/runs/:runId" element={<RunDetailPage />} />
      </Routes>
    </BrowserRouter>
  );
}