from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, Sequence

from app.db.models.tool_execution import ToolExecution, ToolExecutionStatus


class ToolExecutionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        conversation_id: int,
        tool_name: str,
        input_: dict,
        output_: Optional[dict] = None,
        status: ToolExecutionStatus = ToolExecutionStatus.PENDING,
        error: Optional[str] = None,
        duration_ms: Optional[float] = None,
    ) -> ToolExecution:
        execution = ToolExecution(
            conversation_id=conversation_id,
            tool_name=tool_name,
            input_=input_,
            output_=output_,
            status=status,
            error=error,
            duration_ms=duration_ms,
        )
        self.db.add(execution)
        await self.db.flush()
        await self.db.refresh(execution)
        return execution

    async def get_by_id(self, execution_id: int) -> Optional[ToolExecution]:
        result = await self.db.execute(
            select(ToolExecution).where(ToolExecution.id == execution_id)
        )
        return result.scalar_one_or_none()

    async def list_by_conversation(self, conversation_id: int) -> Sequence[ToolExecution]:
        result = await self.db.execute(
            select(ToolExecution)
            .where(ToolExecution.conversation_id == conversation_id)
            .order_by(ToolExecution.created_at.asc())
        )
        return result.scalars().all()

    async def update_status(
        self,
        execution_id: int,
        status: ToolExecutionStatus,
        output_: Optional[dict] = None,
        error: Optional[str] = None,
        duration_ms: Optional[float] = None,
    ) -> Optional[ToolExecution]:
        execution = await self.get_by_id(execution_id)
        if execution:
            execution.status = status
            if output_ is not None:
                execution.output_ = output_
            if error is not None:
                execution.error = error
            if duration_ms is not None:
                execution.duration_ms = duration_ms
            await self.db.flush()
            await self.db.refresh(execution)
        return execution
