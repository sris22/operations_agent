from fastapi import APIRouter, Depends
from app.core.security import get_current_user

router = APIRouter()


@router.get("")
async def list_approvals(current_user=Depends(get_current_user)):
    return {"approvals": []}


@router.get("/{approval_id}")
async def get_approval(approval_id: int, current_user=Depends(get_current_user)):
    return {"approval": None}


@router.post("/{approval_id}/approve")
async def approve_action(approval_id: int, current_user=Depends(get_current_user)):
    return {"message": "Approve - to be implemented"}


@router.post("/{approval_id}/reject")
async def reject_action(approval_id: int, current_user=Depends(get_current_user)):
    return {"message": "Reject - to be implemented"}
