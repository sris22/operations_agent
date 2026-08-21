from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_env: str = "development"
    app_name: str = "ai-customer-operations-agent"

    # Database
    database_url: str

    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # LLM
    llm_provider: str = "openai"
    llm_api_key: str
    llm_model: str = "gpt-4o-mini"

    # Embedding
    embedding_provider: str = "openai"
    embedding_api_key: str
    embedding_model: str = "text-embedding-3-small"

    # Enterprise API
    enterprise_api_base_url: str

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # RAG
    rag_top_k: int = 5
    rag_chunk_size: int = 1000
    rag_chunk_overlap: int = 200

    # Business Rules
    refund_approval_threshold: float = 100.00

    # Timeouts & Limits
    llm_timeout_seconds: int = 60
    external_api_timeout_seconds: int = 30
    max_agent_iterations: int = 10
    max_tool_calls: int = 10
    max_retries: int = 3

    # Logging
    log_level: str = "INFO"

    # Document Upload
    max_upload_size_mb: int = 10
    allowed_document_types: str = "pdf,txt,md"

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def allowed_document_types_list(self) -> list[str]:
        return [t.strip() for t in self.allowed_document_types.split(",") if t.strip()]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
