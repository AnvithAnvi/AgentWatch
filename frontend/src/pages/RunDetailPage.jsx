import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getRun } from "../../api/client";
import SpanCard from "../../components/SpanCard";

export default function RunDetailPage() {
  const { runId } = useParams();

  const [run, setRun] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const runSpans = run?.spans || [];
  const runEvaluations = run?.evaluations || [];
  const errorIndex = runSpans.findIndex((span) => span.status === "error");
  const hasPersistentError = errorIndex >= 0 && runSpans.length > errorIndex + 1;
  const latestEvaluation = runEvaluations.length ? runEvaluations[runEvaluations.length - 1] : null;

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
        <h2>Workflow</h2>

        {runSpans.length === 0 ? (
          <p>No workflow steps were recorded for this run.</p>
        ) : (
          <>
            {hasPersistentError && (
              <div className="error-summary">
                Error started at step {errorIndex + 1} and persisted through downstream workflow steps.
              </div>
            )}

            <div className="workflow-steps">
              {runSpans.map((span, index) => {
                const isError = span.status === "error";
                const hasPersistent = errorIndex >= 0 && index > errorIndex;

                return (
                  <div
                    key={span.id}
                    className={`workflow-step ${isError ? "workflow-error" : hasPersistent ? "workflow-persistent" : ""}`}
                  >
                    <div className="workflow-index">{index + 1}</div>
                    <div className="workflow-body">
                      <div className="workflow-title">
                        <strong>{span.name}</strong>
                        <span className={`status ${span.status}`}>{span.status}</span>
                      </div>

                      <div className="workflow-meta">
                        <span className="badge type-badge">{span.span_type}</span>
                        {span.latency_ms && <span className="latency">{span.latency_ms} ms</span>}
                        {isError && <span className="workflow-flag">Error start</span>}
                        {!isError && hasPersistent && <span className="workflow-flag">Persistent error path</span>}
                      </div>

                      {span.error_message && (
                        <div className="error-box">
                          {span.error_message}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </>
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