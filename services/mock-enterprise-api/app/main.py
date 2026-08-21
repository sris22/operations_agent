from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Mock Enterprise API", version="1.0.0")


class Customer(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    tier: str


class Order(BaseModel):
    id: str
    customer_id: str
    items: list[dict]
    total: float
    status: str


class Payment(BaseModel):
    id: str
    order_id: str
    customer_id: str
    amount: float
    status: str


class Ticket(BaseModel):
    id: str
    customer_id: str
    subject: str
    description: str
    status: str
    priority: str


# In-memory seed data
CUSTOMERS = {
    "CUST-001": Customer(id="CUST-001", name="John Doe", email="john@example.com", phone="555-0101", tier="GOLD"),
    "CUST-002": Customer(id="CUST-002", name="Jane Smith", email="jane@example.com", phone="555-0102", tier="SILVER"),
    "CUST-003": Customer(id="CUST-003", name="Bob Wilson", email="bob@example.com", phone="555-0103", tier="BRONZE"),
}

ORDERS = {
    "ORD-001": Order(id="ORD-001", customer_id="CUST-001", items=[{"name": "Widget A", "qty": 2, "price": 50.0}], total=100.0, status="COMPLETED"),
    "ORD-002": Order(id="ORD-002", customer_id="CUST-001", items=[{"name": "Premium Package", "qty": 1, "price": 299.99}], total=299.99, status="PENDING"),
    "ORD-003": Order(id="ORD-003", customer_id="CUST-002", items=[{"name": "Basic Plan", "qty": 1, "price": 49.99}], total=49.99, status="COMPLETED"),
}

PAYMENTS = {
    "PAY-001": Payment(id="PAY-001", order_id="ORD-001", customer_id="CUST-001", amount=100.0, status="COMPLETED"),
    "PAY-002": Payment(id="PAY-002", order_id="ORD-002", customer_id="CUST-001", amount=299.99, status="COMPLETED"),
    "PAY-003": Payment(id="PAY-003", order_id="ORD-003", customer_id="CUST-002", amount=49.99, status="COMPLETED"),
}

TICKETS = {}
TICKET_COUNTER = 0


@app.get("/customers/{customer_id}", response_model=Customer)
async def get_customer(customer_id: str):
    if customer_id not in CUSTOMERS:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    return CUSTOMERS[customer_id]


@app.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: str):
    if order_id not in ORDERS:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    return ORDERS[order_id]


@app.get("/payments/{payment_id}", response_model=Payment)
async def get_payment(payment_id: str):
    if payment_id not in PAYMENTS:
        raise HTTPException(status_code=404, detail=f"Payment {payment_id} not found")
    return PAYMENTS[payment_id]


@app.post("/payments/{payment_id}/refund")
async def refund_payment(payment_id: str, amount: Optional[float] = None):
    if payment_id not in PAYMENTS:
        raise HTTPException(status_code=404, detail=f"Payment {payment_id} not found")
    payment = PAYMENTS[payment_id]
    if payment.status == "REFUNDED":
        raise HTTPException(status_code=400, detail="Payment already refunded")
    refund_amount = amount if amount else payment.amount
    payment.status = "REFUNDED"
    return {"success": True, "refund_amount": refund_amount, "payment_id": payment_id}


@app.post("/tickets", response_model=Ticket, status_code=201)
async def create_ticket(ticket_data: dict):
    global TICKET_COUNTER
    TICKET_COUNTER += 1
    ticket_id = f"TKT-{TICKET_COUNTER:03d}"
    ticket = Ticket(
        id=ticket_id,
        customer_id=ticket_data["customer_id"],
        subject=ticket_data["subject"],
        description=ticket_data["description"],
        status="OPEN",
        priority=ticket_data.get("priority", "MEDIUM"),
    )
    TICKETS[ticket_id] = ticket
    return ticket


@app.get("/tickets/{ticket_id}", response_model=Ticket)
async def get_ticket(ticket_id: str):
    if ticket_id not in TICKETS:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
    return TICKETS[ticket_id]
