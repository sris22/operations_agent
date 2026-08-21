import structlog

from app.core.config import settings
from app.db.database import async_session
from app.db.repositories.document_chunk_repo import DocumentChunkRepository
from app.db.repositories.document_repo import DocumentRepository
from app.rag.ingestion import ALLOWED_TYPES, ingest_document

logger = structlog.get_logger(__name__)


async def upload_document(
    filename: str,
    file_content: bytes,
    metadata: dict | None = None,
) -> dict:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_TYPES:
        raise ValueError(f"Unsupported file type: {ext}. Allowed: {', '.join(ALLOWED_TYPES)}")

    max_size_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(file_content) > max_size_bytes:
        raise ValueError(f"File too large. Max size: {settings.max_upload_size_mb}MB")

    result = await ingest_document(
        filename=filename,
        file_content=file_content,
        metadata=metadata,
    )

    logger.info(
        "document_uploaded",
        document_id=result["document_id"],
        filename=filename,
        chunk_count=result["chunk_count"],
    )

    return result


async def list_documents(page: int = 1, page_size: int = 20) -> dict:
    async with async_session() as session:
        doc_repo = DocumentRepository(session)
        chunk_repo = DocumentChunkRepository(session)

        documents = await doc_repo.list_documents(page=page, page_size=page_size)
        total = await doc_repo.count()

        doc_list = []
        for doc in documents:
            chunks = await chunk_repo.list_by_document(doc.id)
            doc_list.append(
                {
                    "id": doc.id,
                    "filename": doc.filename,
                    "metadata_": doc.metadata_,
                    "created_at": doc.created_at.isoformat(),
                    "chunk_count": len(chunks),
                }
            )

        return {
            "documents": doc_list,
            "total": total,
            "page": page,
            "page_size": page_size,
        }


async def delete_document(document_id: int) -> bool:
    async with async_session() as session:
        chunk_repo = DocumentChunkRepository(session)
        doc_repo = DocumentRepository(session)

        deleted_chunks = await chunk_repo.delete_by_document(document_id)
        deleted = await doc_repo.delete(document_id)

        if deleted:
            logger.info(
                "document_deleted",
                document_id=document_id,
                chunks_removed=deleted_chunks,
            )

        return deleted
