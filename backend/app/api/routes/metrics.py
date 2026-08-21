from fastapi import APIRouter, Depends
from app.core.security import get_current_user

router = APIRouter()


@router.post("/run")
async def run_evaluation(current_user=Depends(get_current_user)):
    return {"message": "Evaluation run - to be implemented"}


@router.get("")
async def list_evaluations(current_user=Depends(get_current_user)):
    return {"evaluations": []}


@router.get("/{evaluation_id}")
async def get_evaluation(evaluation_id: int, current_user=Depends(get_current_user)):
    return {"evaluation": None}
