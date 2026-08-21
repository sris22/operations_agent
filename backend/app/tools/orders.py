from pydantic import BaseModel, Field

from app.services.enterprise_client import EnterpriseAPIError, EnterpriseClient


class OrderLookupInput(BaseModel):
    order_id: str = Field(..., description="The order ID to look up")


class OrderLookupResult(BaseModel):
    success: bool
    order: dict | None = None
    error_code: str | None = None
    message: str | None = None


async def get_order(client: EnterpriseClient, order_id: str) -> OrderLookupResult:
    try:
        data = await client.get_order(order_id)
        return OrderLookupResult(success=True, order=data)
    except EnterpriseAPIError as e:
        if e.status_code == 404:
            return OrderLookupResult(
                success=False,
                error_code="ORDER_NOT_FOUND",
                message="Order could not be found.",
            )
        return OrderLookupResult(
            success=False,
            error_code="ENTERPRISE_API_ERROR",
            message="Could not retrieve order information.",
        )
