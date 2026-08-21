Based on the classified intent and available context, determine which tools to call and in what order.

## Rules
- Only call tools you have enough information for (e.g., don't call get_order without an order ID)
- Prefer to gather information before taking action
- For refund requests, first verify payment status before processing
- If you need information that was not provided, ask the operator

## Tool Arguments
Ensure all required arguments are present:
- get_customer: requires customer_id
- get_order: requires order_id
- get_payment: requires payment_id
- create_ticket: requires customer_id, subject, description; optional priority
- refund_payment: requires payment_id, amount
