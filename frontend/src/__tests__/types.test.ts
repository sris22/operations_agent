import { describe, it, expect } from "vitest";
import type {
  User,
  ChatRequest,
  ChatResponse,
  Approval,
  DocumentInfo,
  EvaluationRun,
} from "../types";

describe("TypeScript types compile", () => {
  it("User type is valid", () => {
    const user: User = { id: 1, email: "test@test.com", role: "OPERATOR" };
    expect(user.id).toBe(1);
  });

  it("ChatRequest type is valid", () => {
    const req: ChatRequest = { message: "hello" };
    expect(req.message).toBe("hello");
  });

  it("ChatResponse type is valid", () => {
    const res: ChatResponse = {
      conversation_id: 1,
      message_id: 1,
      response: "hi",
      sources: [],
      tool_executions: [],
      approval_required: false,
      approval_id: null,
    };
    expect(res.conversation_id).toBe(1);
  });

  it("Approval type is valid", () => {
    const a: Approval = {
      id: 1,
      conversation_id: 1,
      action_type: "refund",
      action_payload: {},
      status: "PENDING",
      requested_at: "2024-01-01T00:00:00Z",
      resolved_at: null,
      resolved_by: null,
    };
    expect(a.status).toBe("PENDING");
  });

  it("DocumentInfo type is valid", () => {
    const d: DocumentInfo = {
      id: 1,
      filename: "test.pdf",
      metadata_: null,
      created_at: "2024-01-01T00:00:00Z",
      chunk_count: 5,
    };
    expect(d.chunk_count).toBe(5);
  });

  it("EvaluationRun type is valid", () => {
    const e: EvaluationRun = {
      id: 1,
      conversation_id: 1,
      retrieval_score: 0.9,
      relevance_score: 0.8,
      faithfulness_score: 0.85,
      latency_ms: 150,
      estimated_cost: null,
      tool_success_rate: 1.0,
      created_at: "2024-01-01T00:00:00Z",
    };
    expect(e.retrieval_score).toBe(0.9);
  });
});
