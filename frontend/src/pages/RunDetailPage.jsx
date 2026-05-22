import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getRun } from "../../api/client";
import SpanCard from "../../components/SpanCard";

export default function RunDetailPage() {
  const { runId } = useParams();

  const [run, setRun] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const latestEvaluation = run?.evaluations?.[run.evaluations.length - 1] ?? null;

  async function loadRun() {
    try {
      setLoading(true);
      const data = await getRun(runId);
      setRun(data);
    } catch (err) {
      setError("Failed to load run detail.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadRun();
  }, [runId]);

  if (loading) {
    return <div className="page">Loading run...</div>;
  }

  if (error) {
    return <div className="page error">{error}</div>;
  }

  if (!run) {
    return <div className="page">Run not found.</div>;
  }

  return (
    <div className="page">
      <div className="header">
        <div>
          <Link to="/">← Back to runs</Link>
          <h1>{run.run_name}</h1>
          <p>Trace details for this agent execution.</p>
        </div>

        <button onClick={loadRun}>Refresh</button>
      </div>

      <div className="summary-grid">
        <div className="metric-card">
          <span>Status</span>
          <strong>{run.status}</strong>
        </div>

        <div className="metric-card">
          <span>Model</span>
          <strong>{run.model || "-"}</strong>
        </div>

        <div className="metric-card">
          <span>Latency</span>
          <strong>{run.latency_ms ? `${run.latency_ms} ms` : "-"}</strong>
        </div>

        <div className="metric-card">
          <span>Cost</span>
          <strong>{run.cost_usd || "-"}</strong>
        </div>
      </div>

      <div className="card">
        <h2>Input</h2>
        <p>{run.input_text || "-"}</p>
      </div>

      <div className="card">
        <h2>Output</h2>
        <p>{run.output_text || "-"}</p>
      </div>

      <div className="card">
        <h2>Evaluation</h2>

        {latestEvaluation ? (
          <div className="evaluation-card">
            <div className="evaluation-header">
              <span className={`status ${latestEvaluation.label}`}>
                {latestEvaluation.label.toUpperCase()}
              </span>
              <strong>{latestEvaluation.score}/100</strong>
            </div>
            <p>{latestEvaluation.reason}</p>
            <div className="evaluation-metrics">
              <div>
                <strong>Has Error:</strong> {latestEvaluation.has_error}
              </div>
              <div>
                <strong>Tool Failure:</strong> {latestEvaluation.tool_failure}
              </div>
              <div>
                <strong>Latency Warning:</strong> {latestEvaluation.latency_warning}
              </div>
              <div>
                <strong>Empty Output:</strong> {latestEvaluation.empty_output}
              </div>
            </div>
          </div>
        ) : (
          <p>No evaluation available for this run.</p>
        )}
      </div>

      <div className="card">
        <h2>Trace Timeline</h2>
        {run.spans.length === 0 ? (
          <p>No spans recorded.</p>
        ) : (
          <>
            {/* Summary metrics */}
            <div className="span-summary">
              <div className="summary-item">
                <strong>{run.spans.length}</strong>
                <div>Total spans</div>
              </div>
              <div className="summary-item">
                <strong>{run.spans.filter(s => s.status === 'error').length}</strong>
                <div>Failed spans</div>
              </div>
              <div className="summary-item">
                <strong>{run.spans.filter(s => s.span_type === 'tool_call').length}</strong>
                <div>Tool calls</div>
              </div>
              <div className="summary-item">
                <strong>{run.spans.filter(s => s.span_type === 'llm_call').length}</strong>
                <div>LLM calls</div>
              </div>
            </div>

            <div className="timeline">
              {run.spans.map((span, index) => (
                <SpanCard key={span.id} span={span} index={index} />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}