from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Sequence

from app.db.models.approval import Approval, ApprovalStatus


class ApprovalRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        conversation_id: int,
        action_type: str,
        action_payload: dict,
    ) -> Approval:
        approval = Approval(
            conversation_id=conversation_id,
            action_type=action_type,
            action_payload=action_payload,
            status=ApprovalStatus.PENDING,
        )
        self.db.add(approval)
        await self.db.flush()
        await self.db.refresh(approval)
        return approval

    async def get_by_id(self, approval_id: int) -> Optional[Approval]:
        result = await self.db.execute(select(Approval).where(Approval.id == approval_id))
        return result.scalar_one_or_none()

    async def list_pending(self, page: int = 1, page_size: int = 20) -> Sequence[Approval]:
        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(Approval)
            .where(Approval.status == ApprovalStatus.PENDING)
            .order_by(Approval.requested_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        return result.scalars().all()

    async def list_by_conversation(self, conversation_id: int) -> Sequence[Approval]:
        result = await self.db.execute(
            select(Approval)
            .where(Approval.conversation_id == conversation_id)
            .order_by(Approval.requested_at.desc())
        )
        return result.scalars().all()

    async def resolve(
        self,
        approval_id: int,
        status: ApprovalStatus,
        resolved_by: int,
    ) -> Optional[Approval]:
        approval = await self.get_by_id(approval_id)
        if not approval:
            return None
        if approval.status != ApprovalStatus.PENDING:
            return approval
        approval.status = status
        approval.resolved_at = datetime.now(timezone.utc)
        approval.resolved_by = resolved_by
        await self.db.flush()
        await self.db.refresh(approval)
        return approval
