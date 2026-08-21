from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.document_chunk import DocumentChunk


class DocumentChunkRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        document_id: int,
        content: str,
        embedding: str,
        metadata_: dict | None = None,
    ) -> DocumentChunk:
        chunk = DocumentChunk(
            document_id=document_id,
            content=content,
            embedding=embedding,
            metadata_=metadata_,
        )
        self.db.add(chunk)
        await self.db.flush()
        await self.db.refresh(chunk)
        return chunk

    async def create_many(self, chunks: list[DocumentChunk]) -> list[DocumentChunk]:
        self.db.add_all(chunks)
        await self.db.flush()
        for chunk in chunks:
            await self.db.refresh(chunk)
        return chunks

    async def list_by_document(self, document_id: int) -> Sequence[DocumentChunk]:
        result = await self.db.execute(
            select(DocumentChunk).where(DocumentChunk.document_id == document_id)
        )
        return result.scalars().all()

    async def delete_by_document(self, document_id: int) -> int:
        chunks = await self.list_by_document(document_id)
        count = len(chunks)
        for chunk in chunks:
            await self.db.delete(chunk)
        await self.db.flush()
        return count
