from typing import Optional
from pydantic import BaseModel, Field

from app.services.enterprise_client import EnterpriseClient, EnterpriseAPIError


class CreateTicketInput(BaseModel):
    customer_id: str = Field(..., description="The customer ID")
    subject: str = Field(..., min_length=1, max_length=512, description="Ticket subject")
    description: str = Field(..., min_length=1, description="Ticket description")
    priority: str = Field(default="MEDIUM", pattern="^(LOW|MEDIUM|HIGH|URGENT)$", description="Ticket priority")


class CreateTicketResult(BaseModel):
    success: bool
    ticket: Optional[dict] = None
    error_code: Optional[str] = None
    message: Optional[str] = None


async def create_ticket(
    client: EnterpriseClient,
    customer_id: str,
    subject: str,
    description: str,
    priority: str = "MEDIUM",
) -> CreateTicketResult:
    try:
        data = await client.create_ticket(customer_id, subject, description, priority)
        return CreateTicketResult(success=True, ticket=data)
    except EnterpriseAPIError as e:
        if e.status_code == 422:
            return CreateTicketResult(
                success=False,
                error_code="INVALID_INPUT",
                message="Invalid ticket data provided.",
            )
        return CreateTicketResult(
            success=False,
            error_code="ENTERPRISE_API_ERROR",
            message="Could not create ticket.",
        )
