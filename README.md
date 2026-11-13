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

**Key contract** — the two lines the model must return:

```text
Route: <billing or orders>
Reason: <one sentence pointing to what the merchant wrote>
```

## Model

`nvidia/nemotron-3.5-lightning:free` — read from `OPENROUTER_MODEL` in `.env`, same string set as the fallback default in `triage.py`.

## Validation

- Route not in `{billing, orders}` → `ValueError`
- `Reason:` line absent → `ValueError` (no silent fallback)

## Secret Hygiene

`.env` is in `.gitignore` from the first commit. `git log -S "sk-or-v1" --all` returns 0 commits.

## What Was Checked and Changed

- Checked Maria Sousa `SUP-48213` predicted route against `expected_route` (Column J) — both runs returned `orders`, 0 mismatches.
- Checked that the reason cites her actual wording (postage complaint, 40 orders since Saturday, Portugal vs Europe rate inversion).
- Changed `triage.py`: replaced silent `reason = reply` fallback with a strict `ValueError`.

---

## Run Output — Maria Sousa `SUP-48213`

**Expected route**: `orders`

> *"Olá, since saturday my shipping rates are all wrong, buyers in europe pay the domestic portugal rate and buyers in portugal got charged international?? about 40 orders already since the black friday promo started... one customer from Braga paid €14,90 postage for a small mug that costs €4,50 to send inside portugal... obrigada, Maria - Barro Azul Cerâmica"*

**Run 1**

```text
Route              : orders
Expected Route     : orders
Route == Expected? : True (PASS)
Reason             : The merchant reports that broken shipping rates are incorrectly charging domestic buyers international fees and vice versa, directly impacting order fulfillments.
```

**Run 2 (after strict validation change)**

```text
Route              : orders
Expected Route     : orders
Route == Expected? : True (PASS)
Reason             : The merchant states that shipping rates are wrong since Saturday, with European buyers paying domestic Portugal rates while Portugal buyers were charged international rates, directly affecting roughly 40 orders since the Black Friday promo.
```

Both runs: route correct, reason grounded in Maria's message.
