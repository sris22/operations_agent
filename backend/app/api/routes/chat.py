from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from app.core.security import get_current_user
from app.db.database import async_session
from app.db.repositories.conversation_repo import ConversationRepository
from app.db.repositories.message_repo import MessageRepository
from app.services.chat_service import process_message

router = APIRouter()


class ChatRequest(BaseModel):
    conversation_id: int | None = None
    message: str


@router.post("/chat")
async def send_message(
    body: ChatRequest,
    request: Request,
    current_user=Depends(get_current_user),
):
    request_id = getattr(request.state, "request_id", None)

    try:
        result = await process_message(
            user_id=int(current_user["id"]),
            message=body.message,
            conversation_id=body.conversation_id,
            request_id=request_id,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to process message")


@router.get("/conversations")
async def list_conversations(
    page: int = 1,
    page_size: int = 20,
    current_user=Depends(get_current_user),
):
    async with async_session() as session:
        repo = ConversationRepository(session)
        conversations = await repo.list_by_user(
            user_id=int(current_user["id"]),
            page=page,
            page_size=min(page_size, 100),
        )
        total = await repo.count_by_user(int(current_user["id"]))

        return {
            "conversations": [
                {
                    "id": c.id,
                    "customer_id": c.customer_id,
                    "status": c.status.value,
                    "created_at": c.created_at.isoformat(),
                    "updated_at": c.updated_at.isoformat(),
                }
                for c in conversations
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: int,
    current_user=Depends(get_current_user),
):
    async with async_session() as session:
        repo = ConversationRepository(session)
        conversation = await repo.get_by_id(conversation_id)

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        return {
            "id": conversation.id,
            "customer_id": conversation.customer_id,
            "status": conversation.status.value,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
        }


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: int,
    page: int = 1,
    page_size: int = 100,
    current_user=Depends(get_current_user),
):
    async with async_session() as session:
        repo = MessageRepository(session)
        messages = await repo.list_by_conversation(
            conversation_id=conversation_id,
            page=page,
            page_size=min(page_size, 200),
        )

        return {
            "messages": [
                {
                    "id": m.id,
                    "role": m.role.value,
                    "content": m.content,
                    "metadata_": m.metadata_,
                    "created_at": m.created_at.isoformat(),
                }
                for m in messages
            ]
        }
