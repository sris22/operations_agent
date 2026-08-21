import { useState, useEffect } from "react";
import { getEvaluations, runEvaluation } from "../services/api";
import type { EvaluationRun } from "../types";

interface EvalResult {
  evaluation_run_id: number;
  total_cases: number;
  successful_cases: number;
  failed_cases: number;
  average_latency_ms: number;
  retrieval_score: number;
  relevance_score: number;
  faithfulness_score: number;
  tool_success_rate: number;
  results: Array<{
    case_id: string;
    success: boolean;
    latency_ms: number;
    error?: string;
  }>;
}

export default function Evaluations() {
  const [evaluations, setEvaluations] = useState<EvaluationRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [lastResult, setLastResult] = useState<EvalResult | null>(null);

  const loadEvaluations = () => {
    setLoading(true);
    getEvaluations()
      .then((res) => setEvaluations(res.evaluations))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadEvaluations();
  }, []);

  const handleRun = async () => {
    setRunning(true);
    setLastResult(null);
    try {
      const result = await runEvaluation() as unknown as EvalResult;
      setLastResult(result);
      loadEvaluations();
    } catch {
      alert("Evaluation failed");
    } finally {
      setRunning(false);
    }
  };

  const scoreColor = (score: number | null) => {
    if (score === null) return "";
    if (score >= 0.8) return "score-good";
    if (score >= 0.5) return "score-ok";
    return "score-bad";
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h2>Evaluations</h2>
        <button
          className="btn btn-primary"
          onClick={handleRun}
          disabled={running}
        >
          {running ? "Running..." : "Run Evaluation"}
        </button>
      </div>

      {lastResult && (
        <div className="eval-summary">
          <h3>Latest Run #{lastResult.evaluation_run_id}</h3>
          <div className="eval-scores">
            <div className="eval-score-card">
              <span className="score-label">Retrieval</span>
              <span className={`score-value ${scoreColor(lastResult.retrieval_score)}`}>
                {(lastResult.retrieval_score * 100).toFixed(0)}%
              </span>
            </div>
            <div className="eval-score-card">
              <span className="score-label">Relevance</span>
              <span className={`score-value ${scoreColor(lastResult.relevance_score)}`}>
                {(lastResult.relevance_score * 100).toFixed(0)}%
              </span>
            </div>
            <div className="eval-score-card">
              <span className="score-label">Faithfulness</span>
              <span className={`score-value ${scoreColor(lastResult.faithfulness_score)}`}>
                {(lastResult.faithfulness_score * 100).toFixed(0)}%
              </span>
            </div>
            <div className="eval-score-card">
              <span className="score-label">Tool Success</span>
              <span className={`score-value ${scoreColor(lastResult.tool_success_rate)}`}>
                {(lastResult.tool_success_rate * 100).toFixed(0)}%
              </span>
            </div>
            <div className="eval-score-card">
              <span className="score-label">Avg Latency</span>
              <span className="score-value">
                {lastResult.average_latency_ms.toFixed(0)}ms
              </span>
            </div>
            <div className="eval-score-card">
              <span className="score-label">Cases</span>
              <span className="score-value">
                {lastResult.successful_cases}/{lastResult.total_cases}
              </span>
            </div>
          </div>

          <div className="eval-cases">
            <h4>Case Results</h4>
            {lastResult.results.map((r) => (
              <div
                key={r.case_id}
                className={`eval-case ${r.success ? "pass" : "fail"}`}
              >
                <span className="case-id">{r.case_id}</span>
                <span className="case-status">{r.success ? "PASS" : "FAIL"}</span>
                <span className="case-latency">{r.latency_ms.toFixed(0)}ms</span>
                {r.error && <span className="case-error">{r.error}</span>}
              </div>
            ))}
          </div>
        </div>
      )}

      {loading ? (
        <div className="loading">Loading...</div>
      ) : evaluations.length === 0 ? (
        <div className="empty-state">No evaluation runs yet</div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Retrieval</th>
                <th>Relevance</th>
                <th>Faithfulness</th>
                <th>Tool Success</th>
                <th>Latency</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {evaluations.map((e) => (
                <tr key={e.id}>
                  <td>#{e.id}</td>
                  <td className={scoreColor(e.retrieval_score)}>
                    {e.retrieval_score !== null
                      ? `${(e.retrieval_score * 100).toFixed(0)}%`
                      : "-"}
                  </td>
                  <td className={scoreColor(e.relevance_score)}>
                    {e.relevance_score !== null
                      ? `${(e.relevance_score * 100).toFixed(0)}%`
                      : "-"}
                  </td>
                  <td className={scoreColor(e.faithfulness_score)}>
                    {e.faithfulness_score !== null
                      ? `${(e.faithfulness_score * 100).toFixed(0)}%`
                      : "-"}
                  </td>
                  <td className={scoreColor(e.tool_success_rate)}>
                    {e.tool_success_rate !== null
                      ? `${(e.tool_success_rate * 100).toFixed(0)}%`
                      : "-"}
                  </td>
                  <td>{e.latency_ms !== null ? `${e.latency_ms.toFixed(0)}ms` : "-"}</td>
                  <td>{new Date(e.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
