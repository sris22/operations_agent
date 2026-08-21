# Architecture

## System Overview

The AI Customer Operations Agent is a production-style system that allows customer-support operators to submit customer issues and receive AI-powered assistance with tool execution, knowledge retrieval, and human approval workflows.

## Components

### Backend (FastAPI)

- **API Layer** — Route handlers for auth, chat, documents, approvals, tickets, evaluations
- **Service Layer** — Business logic encapsulation
- **Repository Layer** — Database query abstraction
- **Agent Layer** — LangGraph workflow orchestration
- **RAG Layer** — Document ingestion, chunking, embedding, retrieval
- **Tool Layer** — Explicit, testable tool implementations
- **Enterprise Client** — HTTP client for external API communication

### Frontend (React)

- Authentication (login/register)
- Chat interface with agent activity trace
- Approval management
- Document upload and management
- Evaluation dashboard

### Mock Enterprise API

- Separate HTTP service simulating external enterprise systems
- Customer, Order, Payment, Ticket endpoints
- In-memory seed data
- Communicates with backend only via HTTP (no Python imports)

### Database (PostgreSQL + pgvector)

- User authentication and RBAC
- Conversation and message persistence
- Document storage and vector embeddings
- Tool execution logs
- Approval records
- Evaluation run data

## Agent Workflow

```
START
  ↓
classify_request — Determine intent and required tools
  ↓
retrieve_context — RAG vector search for relevant knowledge
  ↓
decide_tools — Select which tools to call based on intent
  ↓
execute_tools — Call tools via enterprise client
  ↓
evaluate_action — Determine if human approval is needed
  ↓
approval_required?
  ├── NO → generate_response
  └── YES → create_approval → WAIT → approval_result → execute_action → generate_response
  ↓
END
```

## Data Flow

1. Operator submits message via frontend
2. Backend authenticates, creates/loads conversation
3. Agent classifies intent
4. RAG retrieves relevant knowledge chunks
5. Agent selects and executes tools (enterprise API calls)
6. If sensitive action → approval workflow
7. Agent generates response with citations
8. All data persisted to PostgreSQL
9. Response returned with full trace

## Security

- JWT authentication with role-based access control
- Backend authorization independent of LLM decisions
- Tool input validation and business rule enforcement
- Prompt injection defense (untrusted content isolation)
- No hardcoded secrets or credentials
- Configurable thresholds for sensitive operations
