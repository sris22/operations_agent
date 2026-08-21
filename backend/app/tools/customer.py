from typing import Optional
from pydantic import BaseModel, Field

from app.services.enterprise_client import EnterpriseClient, EnterpriseAPIError


class CustomerLookupInput(BaseModel):
    customer_id: str = Field(..., description="The customer ID to look up")


class CustomerLookupResult(BaseModel):
    success: bool
    customer: Optional[dict] = None
    error_code: Optional[str] = None
    message: Optional[str] = None


async def get_customer(client: EnterpriseClient, customer_id: str) -> CustomerLookupResult:
    try:
        data = await client.get_customer(customer_id)
        return CustomerLookupResult(success=True, customer=data)
    except EnterpriseAPIError as e:
        if e.status_code == 404:
            return CustomerLookupResult(
                success=False,
                error_code="CUSTOMER_NOT_FOUND",
                message="Customer could not be found.",
            )
        return CustomerLookupResult(
            success=False,
            error_code="ENTERPRISE_API_ERROR",
            message="Could not retrieve customer information.",
        )
