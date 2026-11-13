# ticket-triage

Shopify merchant support ticket triage powered by LangGraph.

## Dataset

24 labelled Shopify merchant support tickets in `data/tickets.jsonl`.

## Triage Prompt

```text
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

**Key contract — the two lines the model must return:**

```text
Route: <billing or orders>
Reason: <one sentence pointing to what the merchant wrote>
```

## Model

`nvidia/nemotron-3.5-lightning:free` — read from `OPENROUTER_MODEL` in `.env`, same string set as the fallback default in `triage.py`.

## Secret Hygiene

Both `OPENROUTER_API_KEY` and `OPENROUTER_MODEL` are read from `.env`. That file is listed in `.gitignore` from the first commit and has never entered git history — `git log -S "sk-or-v1" --all` returns 0 commits.

## Validation

- Route not in `{billing, orders}` → `ValueError`
- `Reason:` line absent → `ValueError` (no silent fallback)

## What Was Checked and Changed

- Checked Maria Sousa `SUP-48213` predicted route against `expected_route` (Column J) — run returned `orders`, matched expected.
- Checked that the reason cites her own words: 40 orders, Saturday, wrong postage rate.
- Changed `triage.py`: replaced silent `reason = reply` fallback with a strict `ValueError`.

---

## Run Output — Maria Sousa SUP-48213

Terminal output from `python run_eval.py`:

```
Ticket ID          : SUP-48213
Merchant Name      : Maria Sousa
Expected Route     : orders

[Graph Output]
Route              : orders
Expected Route     : orders
Route == Expected? : True (PASS)
Reason             : The merchant states that shipping rates have been incorrectly applied to customer orders since Saturday, causing domestic buyers to be charged international rates and vice versa, affecting over 40 orders.
```
