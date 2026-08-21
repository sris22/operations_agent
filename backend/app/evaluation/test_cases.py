EVALUATION_CASES = [
    {
        "id": "TC-001",
        "input": "A customer says their payment was charged but their order was not completed.",
        "expected_intent": "payment_issue",
        "expected_tools": ["get_customer", "get_order", "get_payment"],
        "expected_behavior": "Agent should look up payment and order status, determine if refund is needed, and create approval if amount exceeds threshold.",
    },
    {
        "id": "TC-002",
        "input": "Customer CUST-001 wants a refund for payment PAY-001.",
        "expected_intent": "refund_request",
        "expected_tools": ["get_payment", "refund_payment"],
        "expected_behavior": "Agent should verify payment, check amount against threshold, and either process refund or create approval.",
    },
    {
        "id": "TC-003",
        "input": "Look up order ORD-003 for customer CUST-002.",
        "expected_intent": "order_issue",
        "expected_tools": ["get_order"],
        "expected_behavior": "Agent should look up the order and report its status.",
    },
    {
        "id": "TC-004",
        "input": "Create a support ticket for customer CUST-003 about a billing issue. Priority high.",
        "expected_intent": "ticket_creation",
        "expected_tools": ["create_ticket"],
        "expected_behavior": "Agent should create a ticket with the provided details and priority.",
    },
    {
        "id": "TC-005",
        "input": "What is your refund policy?",
        "expected_intent": "general_inquiry",
        "expected_tools": [],
        "expected_behavior": "Agent should retrieve relevant knowledge from RAG and answer based on company policy documents.",
    },
]


def get_test_cases() -> list[dict]:
    return EVALUATION_CASES


def get_test_case(case_id: str) -> dict | None:
    for case in EVALUATION_CASES:
        if case["id"] == case_id:
            return case
    return None
