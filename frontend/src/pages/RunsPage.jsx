import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getRuns } from "../../api/client";

export default function RunsPage() {
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadRuns() {
    try {
      setLoading(true);
      const data = await getRuns();
      setRuns(data);
    } catch (err) {
      setError("Failed to load runs. Is your FastAPI backend running?");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadRuns();
  }, []);

  if (loading) {
    return <div className="page">Loading runs...</div>;
  }

  if (error) {
    return <div className="page error">{error}</div>;
  }

  const totalRuns = runs.length;
  const passedRuns = runs.filter((run) => run.latest_evaluation_label ? run.latest_evaluation_label === "pass" : run.status === "success").length;
  const warningRuns = runs.filter((run) => run.latest_evaluation_label === "warning").length;
  const failedRuns = runs.filter((run) => run.latest_evaluation_label === "fail" || (!run.latest_evaluation_label && run.status !== "success")).length;
  const averageLatency = runs.filter((run) => run.latency_ms != null).reduce((sum, run) => sum + run.latency_ms, 0) / Math.max(1, runs.filter((run) => run.latency_ms != null).length);

  return (
    <div className="page">
      <div className="header">
        <div>
          <h1>AgentWatch</h1>
          <p>Monitor AI agent runs, tool calls, latency, and failures.</p>
        </div>
        <button onClick={loadRuns}>Refresh</button>
      </div>

      <div className="summary-grid">
        <div className="metric-card">
          <span>Total Runs</span>
          <strong>{totalRuns}</strong>
        </div>
        <div className="metric-card">
          <span>Passed</span>
          <strong>{passedRuns}</strong>
        </div>
        <div className="metric-card">
          <span>Warnings</span>
          <strong>{warningRuns}</strong>
        </div>
        <div className="metric-card">
          <span>Failed</span>
          <strong>{failedRuns}</strong>
        </div>
        <div className="metric-card">
          <span>Average Latency</span>
          <strong>{runs.filter((run) => run.latency_ms != null).length ? `${Math.round(averageLatency)} ms` : "-"}</strong>
        </div>
      </div>

      <div className="card">
        <h2>Agent Runs</h2>

        {runs.length === 0 ? (
          <p>No runs yet. Run your demo agent first.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Run</th>
                <th>Status</th>
                <th>Evaluation</th>
                <th>Model</th>
                <th>Latency</th>
                <th>Cost</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {runs.map((run) => (
                <tr key={run.id}>
                  <td>
                    <Link to={`/runs/${run.id}`}>{run.run_name}</Link>
                  </td>
                  <td>
                    <span className={`status ${run.status}`}>
                      {run.status}
                    </span>
                  </td>
                  <td>
                    {run.latest_evaluation_label ? (
                      <span className={`status ${run.latest_evaluation_label}`}>
                        {run.latest_evaluation_label.toUpperCase()} {run.latest_evaluation_score}
                      </span>
                    ) : (
                      "Not evaluated"
                    )}
                  </td>
                  <td>{run.model || "-"}</td>
                  <td>{run.latency_ms ? `${run.latency_ms} ms` : "-"}</td>
                  <td>{run.cost_usd || "-"}</td>
                  <td>{new Date(run.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}