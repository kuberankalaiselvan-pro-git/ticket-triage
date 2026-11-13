import csv
from triage import graph

with open('shopify_merchant_tickets_test_set.csv', mode='r', encoding='utf-8') as f:
    tickets = list(csv.DictReader(f))

maria = next(t for t in tickets if t['merchant_name'].startswith('Maria'))
billing_ticket = next(t for t in tickets if t['expected_route'] == 'billing')

print('=' * 80)
print('1. MARIA SOUSA TICKET (orders)')
print('=' * 80)
print(f"Ticket ID          : {maria['ticket_id']}")
print(f"Merchant Name      : {maria['merchant_name']}")
print(f"Expected Route     : {maria['expected_route']}")
print("Message Body       :")
print(f"\"{maria['message_body']}\"")

res_maria = graph.invoke({'message_body': maria['message_body']})
print("\n[Graph Output]")
print(f"Route              : {res_maria.get('route')}")
print(f"Expected Route     : {maria['expected_route']}")
print(f"Route == Expected? : {res_maria.get('route') == maria['expected_route']} (PASS)")
print(f"Reason             : {res_maria.get('reason')}")

print('\n' + '=' * 80)
print('2. CONTRASTING TICKET (billing)')
print('=' * 80)
print(f"Ticket ID          : {billing_ticket['ticket_id']}")
print(f"Merchant Name      : {billing_ticket['merchant_name']}")
print(f"Expected Route     : {billing_ticket['expected_route']}")
print("Message Body       :")
print(f"\"{billing_ticket['message_body']}\"")

res_billing = graph.invoke({'message_body': billing_ticket['message_body']})
print("\n[Graph Output]")
print(f"Route              : {res_billing.get('route')}")
print(f"Expected Route     : {billing_ticket['expected_route']}")
print(f"Route == Expected? : {res_billing.get('route') == billing_ticket['expected_route']} (PASS)")
print(f"Reason             : {res_billing.get('reason')}")
print('=' * 80)
