from monday_tool import MondayTool
from normalizer import normalize_item, normalize_deal, normalize_work_order
from bi_engine import compute_work_order_performance, compute_sector_quarter_performance
from agent import parse_question, route_query

DEALS_BOARD_ID = 5026905494  # replace with your actual board ID
WORK_ORDERS_BOARD_ID = 5026905498 # replace with yours

tool = MondayTool()

# Fetch ALL deals using pagination
raw_items = tool.get_all_board_items(DEALS_BOARD_ID)
raw_work_orders = tool.get_all_board_items(WORK_ORDERS_BOARD_ID)

#print(f"\nTotal deals fetched: {len(raw_items)}")
#print(f"\nTotal work orders fetched: {len(raw_work_orders)}")
#print("\nSample raw work order:")
#print(raw_work_orders[0])
structured_deals = []
structured_work_orders = []

for raw in raw_items:
    flattened = normalize_item(raw)
    structured = normalize_deal(flattened)
    structured_deals.append(structured)

for raw in raw_work_orders:
    flattened = normalize_item(raw)
    structured = normalize_work_order(flattened)
    structured_work_orders.append(structured)

#print(f"\nTotal structured work orders: {len(structured_work_orders)}")

#print("\nSample structured work orders:")
#for wo in structured_work_orders[:3]:
#    print(wo)

#print(f"Total structured deals: {len(structured_deals)}")

# Print first 3 deals to verify structure
#print("\nSample structured deals:")
#for deal in structured_deals[:3]:
    #print(deal)

# print("\n===== MINING THIS QUARTER FULL PERFORMANCE =====")
# print(
#     compute_sector_quarter_performance(
#         structured_deals,
#         structured_work_orders,
#         "mining"
#     )
# )

question = "How is mining pipeline this quarter?"

parsed = parse_question(question)

# print("Parsed:", parsed)

result = route_query(
     parsed,
     structured_deals,
     structured_work_orders
 )

# print("\nAgent Result:")
# print(result)
from agent import generate_executive_summary

summary = generate_executive_summary(parsed, result)

print("\nExecutive Summary:")
print(summary)