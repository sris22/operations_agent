# AI Customer Operations Agent

An intelligent customer support system powered by AI agents, RAG (Retrieval-Augmented Generation), and tool-calling capabilities. Built with FastAPI, LangGraph, React, and PostgreSQL.

## Architecture

```
                         ┌──────────────────┐
                         │     React UI     │
                         └────────┬─────────┘
                                  │ HTTP/JSON
                                  ▼
                         ┌──────────────────┐
                         │    FastAPI       │
                         │     Backend      │
                         └────────┬─────────┘
                                  │
                 ┌────────────────┼─────────────────┐
                 │                │                 │
                 ▼                ▼                 ▼
          Authentication      Agent API       Metrics API
                                  │
                                  ▼
                         ┌──────────────────┐
                         │    LangGraph     │
                         │  Agent Workflow  │
                         └────────┬─────────┘
                                  │
                  ┌───────────────┼────────────────┐
                  │               │                │
                  ▼               ▼                ▼
                RAG            Tools          Approval
                  │               │                │
                  ▼               ▼                ▼
             PostgreSQL       REST APIs        PostgreSQL
             + pgvector            │
                                  ▼
                         Mock Enterprise API
```

## Features

- **AI Agent** — LangGraph-based workflow with classification, retrieval, tool execution, and response generation
- **RAG Pipeline** — Document ingestion, chunking, embedding, vector search with pgvector
- **Tool Calling** — Customer lookup, order lookup, payment lookup, ticket creation, refund processing
- **Human-in-the-Loop** — Approval workflow for sensitive actions (refunds above configurable threshold)
- **Authentication** — JWT-based auth with role-based access control (ADMIN, OPERATOR)
- **Mock Enterprise API** — Separate HTTP service simulating external enterprise systems
- **Evaluation System** — Retrieval, generation, and agent evaluation with metrics dashboard
- **Observability** — Request IDs, structured logging, latency tracking
- **Docker** — Fully containerized with Docker Compose

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.x, Alembic |
| Database | PostgreSQL 16 + pgvector |
| AI | LangGraph, OpenAI (configurable provider) |
| Frontend | React 18, TypeScript, Vite |
| Auth | JWT, bcrypt |
| Infrastructure | Docker, Docker Compose, GitHub Actions |
| Testing | pytest, httpx |

## Prerequisites

- Docker & Docker Compose
- An OpenAI API key (or compatible provider)

## Quick Start

```bash
# Clone the repository
git clone https://github.com/sris22/operations_agent.git
cd operations_agent

# Create environment file
cp .env.example .env

# Edit .env and set your API keys
# LLM_API_KEY=your-key
# EMBEDDING_API_KEY=your-key
# JWT_SECRET=your-secure-random-secret

# Start all services
docker compose up --build
```

This starts:
- **Backend** at `http://localhost:8000` (API docs at `/docs`)
- **Frontend** at `http://localhost:5173`
- **PostgreSQL** at `http://localhost:5432`
- **Mock Enterprise API** at `http://localhost:8001`

## Development Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@example.com | admin123 |
| Operator | operator@example.com | operator123 |

These are development-only credentials. Change all passwords before any production deployment.

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Login and receive JWT |
| GET | `/api/auth/me` | Get current user info |
| POST | `/api/chat` | Send a message to the AI agent |
| GET | `/api/conversations` | List conversations |
| GET | `/api/conversations/{id}/messages` | Get conversation messages |
| POST | `/api/documents` | Upload a document (PDF/TXT/MD) |
| GET | `/api/documents` | List uploaded documents |
| DELETE | `/api/documents/{id}` | Delete a document |
| GET | `/api/approvals` | List pending approvals |
| POST | `/api/approvals/{id}/approve` | Approve an action |
| POST | `/api/approvals/{id}/reject` | Reject an action |
| POST | `/api/evaluations/run` | Run evaluation suite |
| GET | `/api/evaluations` | List evaluation runs |
| GET | `/health` | Health check |
| GET | `/health/ready` | Readiness check |

## Database

### Migrations

```bash
# Run migrations
docker compose exec backend alembic upgrade head

# Create a new migration
docker compose exec backend alembic revision --autogenerate -m "description"
```

### Seed Data

Development data is seeded automatically on startup via the `seed` service. To re-seed:

```bash
docker compose run --rm seed
```

This creates:
- Admin and operator users
- Sample knowledge documents (refund policy, troubleshooting guide)

### Mock Enterprise Data

The mock enterprise API includes in-memory seed data:
- 3 customers (CUST-001, CUST-002, CUST-003)
- 3 orders (ORD-001, ORD-002, ORD-003)
- 3 payments (PAY-001, PAY-002, PAY-003)

## End-to-End Scenario

The following flow demonstrates the complete system:

1. Operator logs in with credentials
2. Starts a chat: *"A customer says their payment was charged but their order was not completed"*
3. The AI agent:
   - Classifies the request as a payment issue
   - Retrieves relevant knowledge from uploaded documents
   - Looks up customer, order, and payment data via enterprise API
   - Determines a refund is needed
   - Creates an approval request (if amount exceeds threshold)
4. Operator sees the approval in the Approvals page
5. Operator approves the refund
6. Agent processes the refund and generates a response with citations
7. Complete trace is visible in the chat interface

## Configuration

All configuration is externalized via environment variables. See `.env.example` for all available options.

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | — |
| `JWT_SECRET` | Secret for JWT signing | — |
| `LLM_PROVIDER` | LLM provider (openai) | openai |
| `LLM_MODEL` | Model name | gpt-4o-mini |
| `EMBEDDING_MODEL` | Embedding model | text-embedding-3-small |
| `REFUND_APPROVAL_THRESHOLD` | Amount requiring approval | 100.00 |
| `RAG_CHUNK_SIZE` | Text chunk size | 1000 |
| `RAG_CHUNK_OVERLAP` | Chunk overlap | 200 |
| `RAG_TOP_K` | Number of retrieved chunks | 5 |
| `MAX_AGENT_ITERATIONS` | Agent loop limit | 10 |
| `EXTERNAL_API_TIMEOUT_SECONDS` | Enterprise API timeout | 30 |

## Testing

```bash
# Backend tests (tools, RAG)
cd backend
DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/test_db" \
JWT_SECRET="test-secret" \
LLM_API_KEY="test-key" \
EMBEDDING_API_KEY="test-key" \
ENTERPRISE_API_BASE_URL="http://localhost:8001" \
python -m pytest tests/ -v

# Mock enterprise API tests
cd services/mock-enterprise-api
python -m pytest tests/ -v

# Frontend type check
cd frontend
npx tsc --noEmit

# Frontend build
cd frontend
npm run build
```

## CI/CD

GitHub Actions runs on push/PR to master:

1. **Backend lint** — Ruff check and format
2. **Backend tests** — pytest with PostgreSQL service
3. **Mock API tests** — pytest
4. **Frontend build** — TypeScript check + Vite build
5. **Docker build** — Verify all images build successfully

## Project Structure

```
ai-customer-operations-agent/
├── backend/
│   ├── app/
│   │   ├── api/routes/       # FastAPI route handlers
│   │   ├── core/             # Config, security, logging
│   │   ├── db/               # Models, repositories, seed
│   │   ├── agents/           # LangGraph workflow, nodes, prompts
│   │   ├── rag/              # Chunking, embeddings, retrieval
│   │   ├── tools/            # Customer, order, payment, ticket tools
│   │   ├── services/         # Business logic layer
│   │   ├── schemas/          # Pydantic request/response models
│   │   └── evaluation/       # Test cases and evaluator
│   ├── alembic/              # Database migrations
│   ├── tests/                # Backend tests
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/            # Login, Chat, Approvals, Documents, Evaluations
│   │   ├── hooks/            # Auth context
│   │   ├── services/         # API client
│   │   └── types/            # TypeScript types
│   └── Dockerfile
├── services/
│   └── mock-enterprise-api/  # External enterprise API simulator
├── scripts/                  # Entrypoint and seed scripts
├── .github/workflows/ci.yml  # CI pipeline
├── docker-compose.yml
└── .env.example
```

## Limitations

- Mock enterprise data is in-memory (resets on service restart)
- Single-node deployment (not horizontally scalable)
- LLM provider costs vary based on usage
- Document processing supports PDF, TXT, and Markdown only

## Future Improvements

- Persistent mock data (database-backed)
- WebSocket-based real-time updates
- Multi-tenant support
- Streaming responses
- Advanced evaluation with custom metrics
- Monitoring dashboards (Grafana/Prometheus)
- Document versioning
- Conversation export
