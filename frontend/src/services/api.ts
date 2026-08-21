import axios, { AxiosError } from "axios";
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  User,
  ChatRequest,
  ChatResponse,
  Conversation,
  Message,
  Approval,
  DocumentListResponse,
  EvaluationListResponse,
} from "../types";

const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err: AxiosError<{ detail?: string }>) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export async function register(data: RegisterRequest): Promise<User> {
  const res = await api.post<User>("/auth/register", data);
  return res.data;
}

export async function login(data: LoginRequest): Promise<TokenResponse> {
  const res = await api.post<TokenResponse>("/auth/login", data);
  return res.data;
}

export async function getMe(): Promise<User> {
  const res = await api.get<User>("/auth/me");
  return res.data;
}

export async function sendMessage(req: ChatRequest): Promise<ChatResponse> {
  const res = await api.post<ChatResponse>("/chat", req);
  return res.data;
}

export async function getConversations(
  page = 1,
  pageSize = 20
): Promise<{ conversations: Conversation[]; total: number }> {
  const res = await api.get("/conversations", {
    params: { page, page_size: pageSize },
  });
  return res.data;
}

export async function getConversationMessages(
  conversationId: number
): Promise<{ messages: Message[] }> {
  const res = await api.get(`/conversations/${conversationId}/messages`);
  return res.data;
}

export async function getApprovals(
  page = 1,
  pageSize = 20
): Promise<{ approvals: Approval[]; total: number }> {
  const res = await api.get("/approvals", {
    params: { page, page_size: pageSize },
  });
  return res.data;
}

export async function approveAction(
  approvalId: number
): Promise<{ success: boolean }> {
  const res = await api.post(`/approvals/${approvalId}/approve`);
  return res.data;
}

export async function rejectAction(
  approvalId: number
): Promise<{ success: boolean }> {
  const res = await api.post(`/approvals/${approvalId}/reject`);
  return res.data;
}

export async function getDocuments(
  page = 1,
  pageSize = 20
): Promise<DocumentListResponse> {
  const res = await api.get("/documents", {
    params: { page, page_size: pageSize },
  });
  return res.data;
}

export async function uploadDocument(
  file: File,
  metadata?: Record<string, string>
): Promise<{ document_id: number; filename: string; chunk_count: number }> {
  const formData = new FormData();
  formData.append("file", file);
  if (metadata) {
    formData.append("metadata", JSON.stringify(metadata));
  }
  const res = await api.post("/documents", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}

export async function deleteDocument(
  documentId: number
): Promise<{ success: boolean }> {
  const res = await api.delete(`/documents/${documentId}`);
  return res.data;
}

export async function runEvaluation(): Promise<Record<string, unknown>> {
  const res = await api.post("/evaluations/run");
  return res.data;
}

export async function getEvaluations(
  page = 1,
  pageSize = 20
): Promise<EvaluationListResponse> {
  const res = await api.get("/evaluations", {
    params: { page, page_size: pageSize },
  });
  return res.data;
}

export default api;
