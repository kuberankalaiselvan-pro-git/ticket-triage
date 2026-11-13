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

## Strict Validation & Failure Behavior

To ensure the reason strictly points to the merchant's actual wording rather than falling back to unparsed model text, both `Route:` and `Reason:` lines are strictly validated:
- **Invalid or Missing Route**: Raises `ValueError: Invalid route '<route>' received from model. Expected 'billing' or 'orders'.`
- **Missing Reason Line**: Replaced the previous silent fallback (`reason = reply`) with a strict exception:
  ```
  ValueError: Missing 'Reason:' line in model reply. Expected labelled 'Reason:' line. Full model reply:
  <reply>
  ```

## Route Verification

Route check: predicted route matches expected_route across test evaluations (`orders == orders` for SUP-48213, `billing == billing` for SUP-48197).

## Run Output

Output from running the LangGraph triage workflow (`run_eval.py`) on Maria's ticket alongside a contrasting billing ticket under strict validation:

```text
================================================================================
1. MARIA SOUSA TICKET (orders)
================================================================================
Ticket ID       : SUP-48213
Merchant Name   : Maria Sousa
Expected Route  : orders
Message Body    :
"Olá, since saturday my shipping rates are all wrong, buyers in europe pay the domestic portugal rate and buyers in portugal got charged international?? about 40 orders already since the black friday promo started... I didnt change anything in the settings, só abri a loja de manhã e vi as encomendas assim. one customer from Braga paid €14,90 postage for a small mug that costs €4,50 to send inside portugal, she is very upset and wrote me. and the ones going to France and Germany paid almost nothing for big boxes. please fix before more people buy, I have the cyber monday email going out today at 12h. obrigada, Maria - Barro Azul Cerâmica"

[Graph Output]
Route           : orders
Match Expected? : True
Reason          : The merchant states that shipping rates are wrong since Saturday, with European buyers paying domestic Portugal rates while Portugal buyers were charged international rates, directly affecting roughly 40 orders since the Black Friday promo.

================================================================================
2. CONTRASTING TICKET (billing)
================================================================================
Ticket ID       : SUP-48197
Merchant Name   : Carla Jennings
Expected Route  : billing
Message Body    :
"hi, I uninstalled the ReviewPop app on nov 8 because it was slowing down my product pages and I switched to a different one, but my bill this month still shows ReviewPop at $29. I checked apps and its definitely not installed anymore, I even reinstalled the other one to make sure. I dont want to pay for something I'm not using esp right before black friday when every dollar counts. can you take that off or refund it please. store is northfork coffee, thanks"

[Graph Output]
Route           : billing
Match Expected? : True
Reason          : The merchant is being charged $29 for ReviewPop this month after uninstalling the app and is requesting a refund or charge removal.
================================================================================
```
