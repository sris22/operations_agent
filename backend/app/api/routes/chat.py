from fastapi import APIRouter, Depends
from app.core.security import get_current_user

router = APIRouter()


@router.post("/chat")
async def send_message(current_user=Depends(get_current_user)):
    return {"message": "Chat endpoint - to be implemented"}


@router.get("/conversations")
async def list_conversations(current_user=Depends(get_current_user)):
    return {"conversations": []}


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: int, current_user=Depends(get_current_user)):
    return {"conversation": None}


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(conversation_id: int, current_user=Depends(get_current_user)):
    return {"messages": []}
