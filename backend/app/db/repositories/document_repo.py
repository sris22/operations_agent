from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.document import Document


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, filename: str, content: str, metadata_: dict | None = None) -> Document:
        doc = Document(filename=filename, content=content, metadata_=metadata_)
        self.db.add(doc)
        await self.db.flush()
        await self.db.refresh(doc)
        return doc

    async def get_by_id(self, document_id: int) -> Document | None:
        result = await self.db.execute(select(Document).where(Document.id == document_id))
        return result.scalar_one_or_none()

    async def list_documents(self, page: int = 1, page_size: int = 20) -> Sequence[Document]:
        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(Document).order_by(Document.created_at.desc()).offset(offset).limit(page_size)
        )
        return result.scalars().all()

    async def count(self) -> int:
        result = await self.db.execute(select(func.count(Document.id)))
        return result.scalar_one()

    async def delete(self, document_id: int) -> bool:
        doc = await self.get_by_id(document_id)
        if not doc:
            return False
        await self.db.delete(doc)
        await self.db.flush()
        return True
