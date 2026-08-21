import { useState, useEffect } from "react";
import { getApprovals, approveAction, rejectAction } from "../services/api";
import type { Approval } from "../types";

export default function Approvals() {
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<number | null>(null);

  const loadApprovals = () => {
    setLoading(true);
    getApprovals()
      .then((res) => setApprovals(res.approvals))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadApprovals();
  }, []);

  const handleApprove = async (id: number) => {
    setActionLoading(id);
    try {
      await approveAction(id);
      loadApprovals();
    } catch {
      alert("Failed to approve");
    } finally {
      setActionLoading(null);
    }
  };

  const handleReject = async (id: number) => {
    setActionLoading(id);
    try {
      await rejectAction(id);
      loadApprovals();
    } catch {
      alert("Failed to reject");
    } finally {
      setActionLoading(null);
    }
  };

  const formatPayload = (payload: Record<string, unknown>) => {
    const parts: string[] = [];
    if (payload.payment_id) parts.push(`Payment: ${payload.payment_id}`);
    if (payload.refund_amount) parts.push(`Amount: $${payload.refund_amount}`);
    if (payload.amount) parts.push(`Amount: $${payload.amount}`);
    return parts.join(" | ") || JSON.stringify(payload);
  };

  return (
    <div className="page-container">
      <h2>Approvals</h2>

      {loading ? (
        <div className="loading">Loading...</div>
      ) : approvals.length === 0 ? (
        <div className="empty-state">No pending approvals</div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Conversation</th>
                <th>Action</th>
                <th>Details</th>
                <th>Requested</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {approvals.map((a) => (
                <tr key={a.id}>
                  <td>#{a.id}</td>
                  <td>#{a.conversation_id}</td>
                  <td>{a.action_type}</td>
                  <td className="payload-cell">{formatPayload(a.action_payload)}</td>
                  <td>{new Date(a.requested_at).toLocaleString()}</td>
                  <td>
                    <span className={`status-badge status-${a.status.toLowerCase()}`}>
                      {a.status}
                    </span>
                  </td>
                  <td>
                    {a.status === "PENDING" && (
                      <div className="action-buttons">
                        <button
                          className="btn btn-sm btn-success"
                          onClick={() => handleApprove(a.id)}
                          disabled={actionLoading === a.id}
                        >
                          Approve
                        </button>
                        <button
                          className="btn btn-sm btn-danger"
                          onClick={() => handleReject(a.id)}
                          disabled={actionLoading === a.id}
                        >
                          Reject
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
