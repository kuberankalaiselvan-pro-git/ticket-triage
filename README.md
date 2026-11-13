# ticket-triage

Shopify merchant support ticket triage powered by LangGraph.

## Dataset
Contains 24 labelled Shopify merchant support test tickets in `data/tickets.jsonl` (and `shopify_merchant_tickets_test_set.csv`).

## Triage Prompt

The triage node in `triage.py` queries the OpenRouter LLM using the following prompt:

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

### Key Prompt Excerpt

The core two-line routing and grounding contract enforced on the LLM:

```text
Answer strictly on two labelled lines in this exact format:
Route: <billing or orders>
Reason: <one sentence pointing to what the merchant wrote>
```

## Model Configuration

- **Model**: `nvidia/nemotron-3.5-lightning:free` (OpenRouter active free tier).
- **Environment**: Configured via `OPENROUTER_MODEL` in `.env` and set as the default fallback in `triage.py`.

## Strict Validation & Failure Behavior

To ensure the reason strictly points to the merchant's actual wording rather than falling back to unparsed model text, both `Route:` and `Reason:` lines are strictly validated:
- **Invalid or Missing Route**: Raises `ValueError: Invalid route '<route>' received from model. Expected 'billing' or 'orders'.`
- **Missing Reason Line**: Replaced the previous silent fallback (`reason = reply`) with a strict exception:
  ```text
  ValueError: Missing 'Reason:' line in model reply. Expected labelled 'Reason:' line. Full model reply:
  <reply>
  ```

## Security & Secret Hygiene

- `.env` is listed in `.gitignore` and has been excluded since the repository's initial commit.
- **Git History Audit**: Verified with `git log --all --full-history -- .env` and `git log -S "sk-or-v1" --all`—both return 0 commits, confirming zero API keys or environment files have ever entered git history.

## What Was Checked and Changed

- **What was checked**:
  - Checked the predicted route against Column J (`expected_route`) for Maria Sousa's ticket (`SUP-48213`), verifying that both Run 1 and Run 2 predicted `orders` (0 route mismatches).
  - Checked that the extracted reason directly cites Maria's wording (referencing the 40 orders since Saturday and domestic Portugal vs European shipping rates inverted).
  - Checked the contrasting billing ticket (`SUP-48197` - Carla Jennings), verifying it routed to `billing` as expected.
- **What was changed**:
  - In `triage.py`, replaced the silent reason fallback (`if not reason: reason = reply`) with a strict `ValueError` to ensure that missing or malformed `Reason:` lines fail loudly instead of passing unvalidated text.

## Route Verification & Pass Count

- **Maria Sousa (SUP-48213)**: 2/2 passes (100% match with `expected_route: orders` across both initial run and strict-validation re-run).
- **Carla Jennings (SUP-48197)**: 1/1 pass (100% match with `expected_route: billing`).
- **Total Verification Passes**: 3/3 passes (0 route mismatches, 0 fallback failures).

---

## Run Output

### 1. Maria Sousa's Ticket (`SUP-48213` - Expected Route: `orders`)

**Message Body**:
> *"Olá, since saturday my shipping rates are all wrong, buyers in europe pay the domestic portugal rate and buyers in portugal got charged international?? about 40 orders already since the black friday promo started... I didnt change anything in the settings, só abri a loja de manhã e vi as encomendas assim. one customer from Braga paid €14,90 postage for a small mug that costs €4,50 to send inside portugal, she is very upset and wrote me. and the ones going to France and Germany paid almost nothing for big boxes. please fix before more people buy, I have the cyber monday email going out today at 12h. obrigada, Maria - Barro Azul Cerâmica"*

#### Run 1 (Initial Evaluation)
```text
[Graph Output]
Route              : orders
Expected Route     : orders
Route == Expected? : True (PASS)
Reason             : The merchant reports that broken shipping rates are incorrectly charging domestic buyers international fees and vice versa, directly impacting order fulfillments.
```

#### Run 2 (Re-Run with Strict Validation)
```text
[Graph Output]
Route              : orders
Expected Route     : orders
Route == Expected? : True (PASS)
Reason             : The merchant states that shipping rates are wrong since Saturday, with European buyers paying domestic Portugal rates while Portugal buyers were charged international rates, directly affecting roughly 40 orders since the Black Friday promo.
```

---

### 2. Contrasting Ticket (`SUP-48197` - Expected Route: `billing`)

**Merchant**: Carla Jennings  
**Message Body**:
> *"hi, I uninstalled the ReviewPop app on nov 8 because it was slowing down my product pages and I switched to a different one, but my bill this month still shows ReviewPop at $29. I checked apps and its definitely not installed anymore, I even reinstalled the other one to make sure. I dont want to pay for something I'm not using esp right before black friday when every dollar counts. can you take that off or refund it please. store is northfork coffee, thanks"*

#### Run Output
```text
[Graph Output]
Route              : billing
Expected Route     : billing
Route == Expected? : True (PASS)
Reason             : The merchant is being charged $29 for ReviewPop this month after uninstalling the app and is requesting a refund or charge removal.
```
