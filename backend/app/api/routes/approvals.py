from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

from app.core.security import get_current_user
from app.services.approval_service import (
    list_pending_approvals,
    get_approval,
    approve_action,
    reject_action,
)

router = APIRouter()


class ApprovalAction(BaseModel):
    reason: Optional[str] = None


@router.get("")
async def list_approvals(
    page: int = 1,
    page_size: int = 20,
    current_user=Depends(get_current_user),
):
    return await list_pending_approvals(page=page, page_size=min(page_size, 100))


@router.get("/{approval_id}")
async def get_approval_detail(
    approval_id: int,
    current_user=Depends(get_current_user),
):
    result = await get_approval(approval_id)
    if not result:
        raise HTTPException(status_code=404, detail="Approval not found")
    return result


@router.post("/{approval_id}/approve")
async def approve(
    approval_id: int,
    current_user=Depends(get_current_user),
):
    result = await approve_action(
        approval_id=approval_id,
        resolved_by=int(current_user["id"]),
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/{approval_id}/reject")
async def reject(
    approval_id: int,
    current_user=Depends(get_current_user),
):
    result = await reject_action(
        approval_id=approval_id,
        resolved_by=int(current_user["id"]),
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
