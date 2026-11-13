# ticket-triage

Shopify support ticket triage with LangGraph.

## Dataset
Contains 24 labelled Shopify merchant support test tickets in `data/tickets.jsonl`.

## Triage Prompt

The triage node in `triage.py` uses the following prompt to classify tickets:

```
You are a support ticket triage specialist for Shopify merchants.
Analyze the following merchant support message and categorize it into either 'billing' or 'orders'.

- billing: questions or issues regarding invoices, subscription plans, app charges, refunds for fees/charges, payment processing, and payouts.
- orders: questions or issues regarding customer orders, fulfillments, shipping labels, carrier tracking, customer address updates, and line-item refunds or cancellations.

Answer strictly on two labelled lines in this exact format:
Route: <billing or orders>
Reason: <one sentence pointing to what the merchant wrote>

Merchant Message:
{message_body}
```

## Workflow Architecture

- **Node**: Single LangGraph node called `triage`.
- **Dynamic Routing**: Extracts `Route` and `Reason` dynamically from the model's response; the route is never hardcoded.
- **Strict Validation**: Stops with a clear `ValueError` if the model produces anything other than `billing` or `orders`.
- **Environment**: Reads `OPENROUTER_API_KEY` and `OPENROUTER_MODEL` from `.env`.
