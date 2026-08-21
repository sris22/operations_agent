from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Sequence

from app.db.models.message import Message, MessageRole


class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        conversation_id: int,
        role: MessageRole,
        content: str,
        metadata_: Optional[dict] = None,
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            metadata_=metadata_,
        )
        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)
        return message

    async def get_by_id(self, message_id: int) -> Optional[Message]:
        result = await self.db.execute(select(Message).where(Message.id == message_id))
        return result.scalar_one_or_none()

    async def list_by_conversation(
        self, conversation_id: int, page: int = 1, page_size: int = 100
    ) -> Sequence[Message]:
        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .offset(offset)
            .limit(page_size)
        )
        return result.scalars().all()
