import pytest
from fastapi.testclient import TestClient
from app.main import app, CUSTOMERS, ORDERS, PAYMENTS, TICKETS

client = TestClient(app)


class TestCustomers:
    def test_get_existing_customer(self):
        response = client.get("/customers/CUST-001")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "CUST-001"
        assert data["name"] == "John Doe"
        assert "email" in data
        assert "tier" in data

    def test_get_missing_customer(self):
        response = client.get("/customers/CUST-999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestOrders:
    def test_get_existing_order(self):
        response = client.get("/orders/ORD-001")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "ORD-001"
        assert data["customer_id"] == "CUST-001"
        assert "status" in data
        assert "total" in data

    def test_get_missing_order(self):
        response = client.get("/orders/ORD-999")
        assert response.status_code == 404


class TestPayments:
    def test_get_existing_payment(self):
        response = client.get("/payments/PAY-001")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "PAY-001"
        assert data["amount"] == 100.0
        assert data["status"] == "COMPLETED"

    def test_get_missing_payment(self):
        response = client.get("/payments/PAY-999")
        assert response.status_code == 404


class TestRefund:
    def test_refund_success(self):
        response = client.post("/payments/PAY-003/refund")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["refund_amount"] == 49.99
        PAYMENTS["PAY-003"].status = "COMPLETED"  # reset for other tests

    def test_duplicate_refund(self):
        PAYMENTS["TEST-REFUND"] = type("Payment", (), {
            "id": "TEST-REFUND", "order_id": "ORD-001",
            "customer_id": "CUST-001", "amount": 50.0, "status": "REFUNDED"
        })()
        response = client.post("/payments/TEST-REFUND/refund")
        assert response.status_code == 400
        assert "already refunded" in response.json()["detail"].lower()
        del PAYMENTS["TEST-REFUND"]

    def test_refund_missing_payment(self):
        response = client.post("/payments/PAY-999/refund")
        assert response.status_code == 404


class TestTickets:
    def test_create_ticket(self):
        response = client.post("/tickets", json={
            "customer_id": "CUST-001",
            "subject": "Test issue",
            "description": "This is a test ticket",
            "priority": "HIGH",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["customer_id"] == "CUST-001"
        assert data["subject"] == "Test issue"
        assert data["status"] == "OPEN"
        assert "id" in data

    def test_get_existing_ticket(self):
        response = client.post("/tickets", json={
            "customer_id": "CUST-002",
            "subject": "Another issue",
            "description": "Second test ticket",
        })
        ticket_id = response.json()["id"]
        response = client.get(f"/tickets/{ticket_id}")
        assert response.status_code == 200
        assert response.json()["subject"] == "Another issue"

    def test_get_missing_ticket(self):
        response = client.get("/tickets/TKT-999")
        assert response.status_code == 404
