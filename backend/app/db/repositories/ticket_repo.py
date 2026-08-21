from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Sequence

from app.db.models.ticket import Ticket, TicketStatus, TicketPriority


class TicketRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        customer_id: str,
        subject: str,
        description: str,
        priority: TicketPriority = TicketPriority.MEDIUM,
    ) -> Ticket:
        ticket = Ticket(
            customer_id=customer_id,
            subject=subject,
            description=description,
            priority=priority,
        )
        self.db.add(ticket)
        await self.db.flush()
        await self.db.refresh(ticket)
        return ticket

    async def get_by_id(self, ticket_id: int) -> Optional[Ticket]:
        result = await self.db.execute(select(Ticket).where(Ticket.id == ticket_id))
        return result.scalar_one_or_none()

    async def list_by_customer(self, customer_id: str) -> Sequence[Ticket]:
        result = await self.db.execute(
            select(Ticket)
            .where(Ticket.customer_id == customer_id)
            .order_by(Ticket.created_at.desc())
        )
        return result.scalars().all()

    async def update_status(self, ticket_id: int, status: TicketStatus) -> Optional[Ticket]:
        ticket = await self.get_by_id(ticket_id)
        if ticket:
            ticket.status = status
            await self.db.flush()
            await self.db.refresh(ticket)
        return ticket
