import pytest
import asyncio
from app.services.enterprise_client import get_enterprise_client, EnterpriseAPIError
from app.tools.customer import get_customer
from app.tools.orders import get_order
from app.tools.payments import get_payment, refund_payment
from app.tools.tickets import create_ticket


class FakeClient:
    def __init__(self):
        self.base_url = "http://test"
        self.timeout = 5
        self.request_id = "test"

    async def get_customer(self, customer_id):
        if customer_id == "CUST-001":
            return {"id": "CUST-001", "name": "John Doe", "email": "john@test.com", "tier": "GOLD"}
        raise EnterpriseAPIError(status_code=404, detail="Not found")

    async def get_order(self, order_id):
        if order_id == "ORD-001":
            return {"id": "ORD-001", "customer_id": "CUST-001", "total": 100.0, "status": "COMPLETED"}
        raise EnterpriseAPIError(status_code=404, detail="Not found")

    async def get_payment(self, payment_id):
        if payment_id == "PAY-001":
            return {"id": "PAY-001", "amount": 100.0, "status": "COMPLETED"}
        raise EnterpriseAPIError(status_code=404, detail="Not found")

    async def refund_payment(self, payment_id, amount):
        if payment_id == "PAY-002":
            return {"success": True, "refund_amount": amount}
        raise EnterpriseAPIError(status_code=404, detail="Not found")

    async def create_ticket(self, customer_id, subject, description, priority="MEDIUM"):
        return {"id": "TKT-001", "customer_id": customer_id, "subject": subject, "status": "OPEN"}


@pytest.mark.anyio
async def test_get_customer_success():
    client = FakeClient()
    result = await get_customer(client, "CUST-001")
    assert result.success is True
    assert result.customer["name"] == "John Doe"


@pytest.mark.anyio
async def test_get_customer_not_found():
    client = FakeClient()
    result = await get_customer(client, "CUST-999")
    assert result.success is False
    assert result.error_code == "CUSTOMER_NOT_FOUND"


@pytest.mark.anyio
async def test_get_order_success():
    client = FakeClient()
    result = await get_order(client, "ORD-001")
    assert result.success is True
    assert result.order["status"] == "COMPLETED"


@pytest.mark.anyio
async def test_get_order_not_found():
    client = FakeClient()
    result = await get_order(client, "ORD-999")
    assert result.success is False
    assert result.error_code == "ORDER_NOT_FOUND"


@pytest.mark.anyio
async def test_get_payment_success():
    client = FakeClient()
    result = await get_payment(client, "PAY-001")
    assert result.success is True
    assert result.payment["amount"] == 100.0


@pytest.mark.anyio
async def test_get_payment_not_found():
    client = FakeClient()
    result = await get_payment(client, "PAY-999")
    assert result.success is False
    assert result.error_code == "PAYMENT_NOT_FOUND"


@pytest.mark.anyio
async def test_refund_payment_success():
    client = FakeClient()
    result = await refund_payment(client, "PAY-002", 50.0)
    assert result.success is True
    assert result.refund_amount == 50.0


@pytest.mark.anyio
async def test_refund_exceeds_threshold():
    client = FakeClient()
    result = await refund_payment(client, "PAY-002", 200.0)
    assert result.success is False
    assert result.requires_approval is True
    assert result.error_code == "APPROVAL_REQUIRED"


@pytest.mark.anyio
async def test_create_ticket_success():
    client = FakeClient()
    result = await create_ticket(client, "CUST-001", "Test Issue", "Description here")
    assert result.success is True
    assert result.ticket["status"] == "OPEN"


@pytest.mark.anyio
async def test_create_ticket_invalid_input():
    client = FakeClient()
    result = await create_ticket(client, "", "", "")
    assert result.success is True
