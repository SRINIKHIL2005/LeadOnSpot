import { useState } from "react";
import LeadForm from "./components/LeadForm";
import ScoreResult from "./components/ScoreResult";
import "./App.css";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(leadData) {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      let res;
      try {
        res = await fetch(`${API_URL}/score`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(leadData),
        });
      } catch {
        throw new Error("Unable to reach the scoring service. Check that the backend is running and try again.");
      }

      let data;
      try {
        data = await res.json();
      } catch {
        throw new Error(`The scoring service returned an invalid response (HTTP ${res.status}).`);
      }

      if (!res.ok) {
        throw new Error(
          getApiErrorMessage(data && data.detail) || `Scoring failed (HTTP ${res.status}).`
        );
      }

      if (!isScoreResponse(data)) {
        throw new Error("The scoring service returned an unexpected response. Please try again.");
      }

      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unexpected error occurred. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🎯 LeadOnSpot</h1>
        <p>AI-Powered Lead Scoring Agent</p>
      </header>
      <main className="app-main">
        <LeadForm onSubmit={handleSubmit} loading={loading} />
        {error && <div className="error-box" role="alert">⚠️ {error}</div>}
        {result && <ScoreResult result={result} />}
      </main>
    </div>
  );
}

function getApiErrorMessage(detail) {
  if (typeof detail === "string") return detail;
  if (!Array.isArray(detail)) return null;

  const messages = detail
    .map((item) => {
      if (typeof item === "string") return item;
      return item && typeof item.msg === "string" ? item.msg : null;
    })
    .filter(Boolean);

  return messages.length ? messages.join(" ") : null;
}

function isScoreResponse(data) {
  return (
    data &&
    typeof data === "object" &&
    typeof data.score === "number" &&
    typeof data.classification === "string" &&
    typeof data.explanation === "string" &&
    typeof data.explanation_provider === "string" &&
    typeof data.explanation_model === "string" &&
    Array.isArray(data.positive_factors) &&
    Array.isArray(data.negative_factors) &&
    data.score_breakdown &&
    typeof data.score_breakdown === "object"
  );
}
