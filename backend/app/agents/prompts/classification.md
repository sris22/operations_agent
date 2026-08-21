Classify the customer support request into an intent category and determine what tools are needed.

## Intent Categories
- payment_issue: Customer reports a payment problem (charged but not completed, wrong amount, etc.)
- order_issue: Customer has a problem with their order (missing, damaged, wrong item, etc.)
- refund_request: Customer is requesting a refund
- account_issue: Customer has an account-related problem
- general_inquiry: General question that does not require specific tool calls
- ticket_creation: Request to create a support ticket

## Output
Return a JSON object with:
- intent: The classified intent
- requires_tools: Whether any tools need to be called
- tool_calls: List of tool calls with their arguments (if known from the message)
- customer_id: Customer ID if mentioned
- confidence: How confident you are in the classification (0.0 to 1.0)
- reasoning: Brief explanation of your classification
