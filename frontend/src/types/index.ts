export interface User {
  id: number;
  email: string;
  role: "ADMIN" | "OPERATOR";
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  role?: "ADMIN" | "OPERATOR";
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  role: string;
  email: string;
}

export interface ChatRequest {
  conversation_id?: number;
  message: string;
}

export interface SourceInfo {
  content: string;
  document_name: string;
  similarity_score: number;
  metadata: Record<string, unknown>;
}

export interface ToolExecutionInfo {
  tool_name: string;
  status: string;
  duration_ms?: number;
}

export interface ChatResponse {
  conversation_id: number;
  message_id: number;
  response: string;
  sources: SourceInfo[];
  tool_executions: ToolExecutionInfo[];
  approval_required: boolean;
  approval_id: number | null;
}

export interface Conversation {
  id: number;
  customer_id: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: number;
  role: "USER" | "ASSISTANT" | "TOOL" | "SYSTEM";
  content: string;
  metadata_: Record<string, unknown> | null;
  created_at: string;
}

export interface Approval {
  id: number;
  conversation_id: number;
  action_type: string;
  action_payload: Record<string, unknown>;
  status: "PENDING" | "APPROVED" | "REJECTED" | "EXPIRED";
  requested_at: string;
  resolved_at: string | null;
  resolved_by: number | null;
}

export interface DocumentInfo {
  id: number;
  filename: string;
  metadata_: Record<string, unknown> | null;
  created_at: string;
  chunk_count: number;
}

export interface DocumentListResponse {
  documents: DocumentInfo[];
  total: number;
  page: number;
  page_size: number;
}

export interface EvaluationRun {
  id: number;
  conversation_id: number;
  retrieval_score: number | null;
  relevance_score: number | null;
  faithfulness_score: number | null;
  latency_ms: number | null;
  estimated_cost: number | null;
  tool_success_rate: number | null;
  created_at: string;
}

export interface EvaluationListResponse {
  evaluations: EvaluationRun[];
  total: number;
  page: number;
  page_size: number;
}


