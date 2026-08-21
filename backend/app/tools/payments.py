from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.enterprise_client import EnterpriseAPIError, EnterpriseClient


class PaymentLookupInput(BaseModel):
    payment_id: str = Field(..., description="The payment ID to look up")


class PaymentLookupResult(BaseModel):
    success: bool
    payment: dict | None = None
    error_code: str | None = None
    message: str | None = None


async def get_payment(client: EnterpriseClient, payment_id: str) -> PaymentLookupResult:
    try:
        data = await client.get_payment(payment_id)
        return PaymentLookupResult(success=True, payment=data)
    except EnterpriseAPIError as e:
        if e.status_code == 404:
            return PaymentLookupResult(
                success=False,
                error_code="PAYMENT_NOT_FOUND",
                message="Payment could not be found.",
            )
        return PaymentLookupResult(
            success=False,
            error_code="ENTERPRISE_API_ERROR",
            message="Could not retrieve payment information.",
        )


class RefundPaymentInput(BaseModel):
    payment_id: str = Field(..., description="The payment ID to refund")
    amount: float = Field(..., gt=0, description="The refund amount")


class RefundPaymentResult(BaseModel):
    success: bool
    refund_amount: float | None = None
    payment_id: str | None = None
    requires_approval: bool = False
    error_code: str | None = None
    message: str | None = None


async def refund_payment(
    client: EnterpriseClient, payment_id: str, amount: float
) -> RefundPaymentResult:
    if amount > settings.refund_approval_threshold:
        return RefundPaymentResult(
            success=False,
            requires_approval=True,
            error_code="APPROVAL_REQUIRED",
            message=f"Refund of ${amount:.2f} exceeds threshold of ${settings.refund_approval_threshold:.2f}. Approval required.",
        )

    try:
        data = await client.refund_payment(payment_id, amount)
        return RefundPaymentResult(
            success=True,
            refund_amount=data.get("refund_amount", amount),
            payment_id=payment_id,
        )
    except EnterpriseAPIError as e:
        if e.status_code == 400:
            return RefundPaymentResult(
                success=False,
                error_code="PAYMENT_ALREADY_REFUNDED",
                message="This payment has already been refunded.",
            )
        if e.status_code == 404:
            return RefundPaymentResult(
                success=False,
                error_code="PAYMENT_NOT_FOUND",
                message="Payment could not be found.",
            )
        return RefundPaymentResult(
            success=False,
            error_code="ENTERPRISE_API_ERROR",
            message="Could not process refund.",
        )
