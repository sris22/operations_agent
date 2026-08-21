from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.ticket import Ticket, TicketPriority, TicketStatus


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

    async def get_by_id(self, ticket_id: int) -> Ticket | None:
        result = await self.db.execute(select(Ticket).where(Ticket.id == ticket_id))
        return result.scalar_one_or_none()

    async def list_by_customer(self, customer_id: str) -> Sequence[Ticket]:
        result = await self.db.execute(
            select(Ticket)
            .where(Ticket.customer_id == customer_id)
            .order_by(Ticket.created_at.desc())
        )
        return result.scalars().all()

    async def update_status(self, ticket_id: int, status: TicketStatus) -> Ticket | None:
        ticket = await self.get_by_id(ticket_id)
        if ticket:
            ticket.status = status
            await self.db.flush()
            await self.db.refresh(ticket)
        return ticket
