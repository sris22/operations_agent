import structlog
from datetime import datetime, timezone

from app.db.database import async_session
from app.db.repositories.approval_repo import ApprovalRepository
from app.db.models.approval import ApprovalStatus

logger = structlog.get_logger(__name__)


async def list_pending_approvals(page: int = 1, page_size: int = 20) -> dict:
    async with async_session() as session:
        repo = ApprovalRepository(session)
        approvals = await repo.list_pending(page=page, page_size=page_size)
        return {
            "approvals": [
                {
                    "id": a.id,
                    "conversation_id": a.conversation_id,
                    "action_type": a.action_type,
                    "action_payload": a.action_payload,
                    "status": a.status.value,
                    "requested_at": a.requested_at.isoformat(),
                    "resolved_at": a.resolved_at.isoformat() if a.resolved_at else None,
                    "resolved_by": a.resolved_by,
                }
                for a in approvals
            ]
        }


async def get_approval(approval_id: int) -> dict | None:
    async with async_session() as session:
        repo = ApprovalRepository(session)
        approval = await repo.get_by_id(approval_id)
        if not approval:
            return None
        return {
            "id": approval.id,
            "conversation_id": approval.conversation_id,
            "action_type": approval.action_type,
            "action_payload": approval.action_payload,
            "status": approval.status.value,
            "requested_at": approval.requested_at.isoformat(),
            "resolved_at": approval.resolved_at.isoformat() if approval.resolved_at else None,
            "resolved_by": approval.resolved_by,
        }


async def approve_action(approval_id: int, resolved_by: int) -> dict:
    async with async_session() as session:
        repo = ApprovalRepository(session)
        existing = await repo.get_by_id(approval_id)

        if not existing:
            return {"success": False, "error": "Approval not found"}

        if existing.status != ApprovalStatus.PENDING:
            return {
                "success": False,
                "error": f"Approval already {existing.status.value.lower()}",
            }

        approval = await repo.resolve(
            approval_id=approval_id,
            status=ApprovalStatus.APPROVED,
            resolved_by=resolved_by,
        )
        await session.commit()

        logger.info(
            "approval_approved",
            approval_id=approval_id,
            resolved_by=resolved_by,
        )

        return {"success": True, "approval_id": approval_id}


async def reject_action(approval_id: int, resolved_by: int) -> dict:
    async with async_session() as session:
        repo = ApprovalRepository(session)
        existing = await repo.get_by_id(approval_id)

        if not existing:
            return {"success": False, "error": "Approval not found"}

        if existing.status != ApprovalStatus.PENDING:
            return {
                "success": False,
                "error": f"Approval already {existing.status.value.lower()}",
            }

        approval = await repo.resolve(
            approval_id=approval_id,
            status=ApprovalStatus.REJECTED,
            resolved_by=resolved_by,
        )
        await session.commit()

        logger.info(
            "approval_rejected",
            approval_id=approval_id,
            resolved_by=resolved_by,
        )

        return {"success": True, "approval_id": approval_id}
