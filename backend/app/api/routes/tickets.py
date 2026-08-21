from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.security import get_current_user
from app.db.database import async_session
from app.db.repositories.ticket_repo import TicketRepository

router = APIRouter()


class TicketCreate(BaseModel):
    customer_id: str = Field(..., min_length=1)
    subject: str = Field(..., min_length=1, max_length=512)
    description: str = Field(..., min_length=1)
    priority: str = Field(default="MEDIUM", pattern="^(LOW|MEDIUM|HIGH|URGENT)$")


@router.get("")
async def list_tickets(
    customer_id: str | None = None,
    page: int = 1,
    page_size: int = 20,
    current_user=Depends(get_current_user),
):
    async with async_session() as session:
        repo = TicketRepository(session)
        if customer_id:
            tickets = await repo.list_by_customer(customer_id)
        else:
            tickets = []
        return {
            "tickets": [
                {
                    "id": t.id,
                    "customer_id": t.customer_id,
                    "subject": t.subject,
                    "description": t.description,
                    "status": t.status.value,
                    "priority": t.priority.value,
                    "created_at": t.created_at.isoformat(),
                }
                for t in tickets
            ]
        }


@router.get("/{ticket_id}")
async def get_ticket(ticket_id: int, current_user=Depends(get_current_user)):
    async with async_session() as session:
        repo = TicketRepository(session)
        ticket = await repo.get_by_id(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return {
            "id": ticket.id,
            "customer_id": ticket.customer_id,
            "subject": ticket.subject,
            "description": ticket.description,
            "status": ticket.status.value,
            "priority": ticket.priority.value,
            "created_at": ticket.created_at.isoformat(),
        }
