export default function SpanCard({ span, index }) {
  const isError = span.status === "error";

  return (
    <div className={`span-card ${isError ? "span-error" : ""}`}>
      <div className="span-header">
        <div>
          <span className="span-index">Step {index + 1}</span>
          <h3>{span.name}</h3>
        </div>

        <div className="span-meta">
          <span className={`badge type-badge`}>{span.span_type}</span>
          <span className={`badge status-badge ${span.status}`}>{span.status}</span>
          {span.latency_ms && <span className="latency">{span.latency_ms} ms</span>}
        </div>
      </div>

      {span.error_message && (
        <div className="error-box">
          {span.error_message}
        </div>
      )}

      <div className="json-grid">
        <div>
          <h4>Input</h4>
          <pre className="json-pre">{formatJson(span.input_json)}</pre>
        </div>

        <div>
          <h4>Output</h4>
          <pre className="json-pre">{formatJson(span.output_json)}</pre>
        </div>
      </div>
    </div>
  );
}

function formatJson(value) {
  if (!value) return "-";

  try {
    return JSON.stringify(JSON.parse(value), null, 2);
  } catch {
    return value;
  }
}