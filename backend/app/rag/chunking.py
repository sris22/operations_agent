from app.core.config import settings


def chunk_text(text: str, chunk_size: int | None = None, chunk_overlap: int | None = None) -> list[str]:
    chunk_size = chunk_size or settings.rag_chunk_size
    chunk_overlap = chunk_overlap or settings.rag_chunk_overlap

    if not text or not text.strip():
        return []

    cleaned = text.strip()

    if len(cleaned) <= chunk_size:
        return [cleaned]

    chunks = []
    start = 0

    while start < len(cleaned):
        end = start + chunk_size

        if end < len(cleaned):
            last_space = cleaned.rfind(" ", start, end)
            if last_space > start:
                end = last_space

        chunk = cleaned[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - chunk_overlap
        if start >= len(cleaned):
            break

    return chunks
