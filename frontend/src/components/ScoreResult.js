const CLASS_COLORS = { Hot: "#e53e3e", Warm: "#dd6b20", Cold: "#3182ce" };
const CLASS_BG = { Hot: "#fff5f5", Warm: "#fffaf0", Cold: "#ebf8ff" };

export default function ScoreResult({ result }) {
  const color = CLASS_COLORS[result.classification] || "#666";
  const bg = CLASS_BG[result.classification] || "#f9f9f9";

  return (
    <div className="result-card">
      {/* Header */}
      <div className="result-header" style={{ borderColor: color }}>
        <div>
          <h2>{result.lead_name}</h2>
          <p className="company-name">{result.company}</p>
        </div>
        <div className="score-badge" style={{ background: color }}>
          <span className="score-number">{result.score}</span>
          <span className="score-label">/ 100</span>
        </div>
      </div>

      {/* Classification + Quality */}
      <div className="tags-row">
        <span className="tag" style={{ background: bg, color, border: `1px solid ${color}` }}>
          🔥 {result.classification} Lead
        </span>
        <span className="tag tag-quality">{result.quality_assessment}</span>
        <span className="tag tag-confidence">Confidence: {result.confidence}%</span>
      </div>

      {/* Explanation */}
      <div className="section">
        <h3>📋 Scoring Explanation</h3>
        <p className="explanation">{result.explanation}</p>
      </div>

      {/* Score Breakdown */}
      <div className="section">
        <h3>📊 Score Breakdown</h3>
        <div className="breakdown-grid">
          {Object.entries(result.score_breakdown).map(([key, val]) => (
            <div className="breakdown-item" key={key}>
              <div className="breakdown-top">
                <span className="breakdown-label">{formatKey(key)}</span>
                <span className="breakdown-weight">{val.weight}</span>
                <span className="breakdown-score" style={{ color: scoreColor(val.score) }}>
                  {val.score}/100
                </span>
              </div>
              <div className="breakdown-bar-bg">
                <div
                  className="breakdown-bar-fill"
                  style={{ width: `${val.score}%`, background: scoreColor(val.score) }}
                />
              </div>
              <p className="breakdown-detail">{val.detail}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Positive / Negative Factors */}
      <div className="factors-row">
        <div className="factors-box positive">
          <h3>✅ Positive Factors</h3>
          {result.positive_factors.length > 0 ? (
            <ul>{result.positive_factors.map((f, i) => <li key={i}>{f}</li>)}</ul>
          ) : (
            <p className="no-factors">None identified</p>
          )}
        </div>
        <div className="factors-box negative">
          <h3>⚠️ Negative Factors</h3>
          {result.negative_factors.length > 0 ? (
            <ul>{result.negative_factors.map((f, i) => <li key={i}>{f}</li>)}</ul>
          ) : (
            <p className="no-factors">None identified</p>
          )}
        </div>
      </div>

      {/* Next Action */}
      <div className="next-action" style={{ borderColor: color }}>
        <h3>🚀 Recommended Next Action</h3>
        <p>{result.next_action}</p>
      </div>
    </div>
  );
}

function formatKey(key) {
  return key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function scoreColor(score) {
  if (score >= 70) return "#38a169";
  if (score >= 40) return "#dd6b20";
  return "#e53e3e";
}
