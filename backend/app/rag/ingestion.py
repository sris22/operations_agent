import io

import structlog

from app.db.database import async_session
from app.db.models.document_chunk import DocumentChunk
from app.db.repositories.document_chunk_repo import DocumentChunkRepository
from app.db.repositories.document_repo import DocumentRepository
from app.rag.chunking import chunk_text
from app.rag.embeddings import get_embedding_provider

logger = structlog.get_logger(__name__)

ALLOWED_TYPES = {"pdf", "txt", "md"}


def extract_text_from_pdf(content: bytes) -> str:
    from PyPDF2 import PdfReader

    reader = PdfReader(io.BytesIO(content))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n\n".join(pages)


def extract_text(filename: str, content: bytes) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext == "pdf":
        return extract_text_from_pdf(content)
    elif ext in ("txt", "md"):
        return content.decode("utf-8", errors="replace")
    else:
        raise ValueError(f"Unsupported file type: {ext}")


async def ingest_document(
    filename: str,
    file_content: bytes,
    metadata: dict | None = None,
) -> dict:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_TYPES:
        raise ValueError(f"Unsupported file type: {ext}. Allowed: {', '.join(ALLOWED_TYPES)}")

    text_content = extract_text(filename, file_content)
    if not text_content.strip():
        raise ValueError("Document contains no extractable text")

    chunks = chunk_text(text_content)
    if not chunks:
        raise ValueError("No valid chunks could be created from the document")

    provider = get_embedding_provider()
    embeddings = await provider.embed_batch(chunks)

    async with async_session() as session:
        doc_repo = DocumentRepository(session)
        chunk_repo = DocumentChunkRepository(session)

        doc = await doc_repo.create(filename=filename, content=text_content, metadata_=metadata)

        db_chunks = []
        for i, (chunk_text_content, embedding) in enumerate(zip(chunks, embeddings)):
            db_chunks.append(
                DocumentChunk(
                    document_id=doc.id,
                    content=chunk_text_content,
                    embedding=embedding,
                    metadata_={"chunk_index": i, **(metadata or {})},
                )
            )

        await chunk_repo.create_many(db_chunks)
        await session.commit()

        logger.info(
            "document_ingested",
            document_id=doc.id,
            filename=filename,
            chunk_count=len(chunks),
        )

        return {
            "document_id": doc.id,
            "filename": filename,
            "chunk_count": len(chunks),
        }
