import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.database import async_session
from app.db.repositories.document_repo import DocumentRepository
from app.rag.embeddings import get_embedding_provider

logger = structlog.get_logger(__name__)


class RetrievedChunk:
    def __init__(
        self,
        content: str,
        document_name: str,
        similarity_score: float,
        metadata: dict | None = None,
    ):
        self.content = content
        self.document_name = document_name
        self.similarity_score = similarity_score
        self.metadata = metadata or {}

    def to_dict(self) -> dict:
        return {
            "content": self.content,
            "document_name": self.document_name,
            "similarity_score": round(self.similarity_score, 4),
            "metadata": self.metadata,
        }


async def retrieve_relevant_chunks(query: str, top_k: int | None = None) -> list[RetrievedChunk]:
    top_k = top_k or settings.rag_top_k

    provider = get_embedding_provider()
    query_embedding = await provider.embed_text(query)

    async with async_session() as session:
        doc_repo = DocumentRepository(session)
        results = await _vector_search(session, query_embedding, top_k)

        chunks = []
        for row in results:
            doc = await doc_repo.get_by_id(row["document_id"])
            doc_name = doc.filename if doc else "unknown"

            chunks.append(
                RetrievedChunk(
                    content=row["content"],
                    document_name=doc_name,
                    similarity_score=row["similarity"],
                    metadata=row.get("metadata", {}),
                )
            )

        logger.info(
            "rag_retrieval",
            query_length=len(query),
            chunks_found=len(chunks),
            top_k=top_k,
        )

        return chunks


async def _vector_search(
    session: AsyncSession, query_embedding: list[float], top_k: int
) -> list[dict]:
    import numpy as np

    query_vec = np.array(query_embedding, dtype=np.float32).tolist()

    query = text("""
        SELECT
            id,
            document_id,
            content,
            metadata,
            1 - (embedding <=> :embedding::vector) AS similarity
        FROM document_chunks
        ORDER BY embedding <=> :embedding::vector
        LIMIT :limit
    """)

    result = await session.execute(query, {"embedding": str(query_vec), "limit": top_k})
    rows = result.mappings().all()

    return [
        {
            "id": row["id"],
            "document_id": row["document_id"],
            "content": row["content"],
            "metadata": row["metadata"],
            "similarity": float(row["similarity"]),
        }
        for row in rows
    ]


def build_rag_context(chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return "No relevant company knowledge was found for this query."

    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(
            f"[Source {i}: {chunk.document_name} (relevance: {chunk.similarity_score:.2f})]\n"
            f"{chunk.content}"
        )

    return "\n\n---\n\n".join(parts)
