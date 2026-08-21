from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.conversation import Conversation, ConversationStatus


class ConversationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: int, customer_id: str | None = None) -> Conversation:
        conversation = Conversation(user_id=user_id, customer_id=customer_id)
        self.db.add(conversation)
        await self.db.flush()
        await self.db.refresh(conversation)
        return conversation

    async def get_by_id(self, conversation_id: int) -> Conversation | None:
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def list_by_user(
        self, user_id: int, page: int = 1, page_size: int = 20
    ) -> Sequence[Conversation]:
        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        return result.scalars().all()

    async def count_by_user(self, user_id: int) -> int:
        result = await self.db.execute(
            select(func.count(Conversation.id)).where(Conversation.user_id == user_id)
        )
        return result.scalar_one()

    async def update_status(
        self, conversation_id: int, status: ConversationStatus
    ) -> Conversation | None:
        conversation = await self.get_by_id(conversation_id)
        if conversation:
            conversation.status = status
            await self.db.flush()
            await self.db.refresh(conversation)
        return conversation
