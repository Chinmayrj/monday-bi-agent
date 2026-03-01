import streamlit as st
from monday_tool import MondayTool
from normalizer import normalize_item, normalize_deal, normalize_work_order
from agent import (
    parse_question,
    route_query,
    generate_executive_summary,
    needs_clarification
)


# -------------------------------------------------
# Page Config
# -------------------------------------------------

st.set_page_config(page_title="Monday BI Agent", layout="wide")

st.title("📊 Monday.com AI BI Agent")
st.markdown("Ask founder-level business questions about Deals and Work Orders.")

# -------------------------------------------------
# Conversation Memory
# -------------------------------------------------

if "conversation_context" not in st.session_state:
    st.session_state.conversation_context = {}

# -------------------------------------------------
# Board IDs
# -------------------------------------------------

DEALS_BOARD_ID = 5026905494
WORK_ORDERS_BOARD_ID = 5026905498

# -------------------------------------------------
# User Input
# -------------------------------------------------

user_question = st.text_input("Ask your question:")

if user_question:

    tool_logs = []

    # -------------------------------------------------
    # Parse Question FIRST (Before API Calls)
    # -------------------------------------------------

    tool_logs.append("Parsing user question...")
    parsed = parse_question(user_question)
    tool_logs.append(f"Parsed intent: {parsed}")

    # -------------------------------------------------
    # Fill Missing Fields From Context (Follow-up Support)
    # -------------------------------------------------

    context = st.session_state.conversation_context

    if not parsed["sector"] and context.get("sector"):
        parsed["sector"] = context["sector"]

    if not parsed["timeframe"] and context.get("timeframe"):
        parsed["timeframe"] = context["timeframe"]

    if not parsed["intent"] and context.get("intent"):
        parsed["intent"] = context["intent"]

    # -------------------------------------------------
    # Clarification Check (Before Expensive API Calls)
    # -------------------------------------------------

    clarification = needs_clarification(parsed)

    if clarification:
        st.warning(clarification)
        st.stop()

    # Save updated context
    st.session_state.conversation_context.update(parsed)

    # -------------------------------------------------
    # Now Fetch Data (Only After Clarification Passes)
    # -------------------------------------------------

    tool = MondayTool()

    tool_logs.append("Fetching Deals from Monday API (with pagination)...")
    raw_deals = tool.get_all_board_items(DEALS_BOARD_ID)

    structured_deals = []
    for raw in raw_deals:
        flat = normalize_item(raw)
        structured = normalize_deal(flat)
        structured_deals.append(structured)

    tool_logs.append(f"Fetched {len(structured_deals)} deals.")

    tool_logs.append("Fetching Work Orders from Monday API (with pagination)...")
    raw_work_orders = tool.get_all_board_items(WORK_ORDERS_BOARD_ID)

    structured_work_orders = []
    for raw in raw_work_orders:
        flat = normalize_item(raw)
        structured = normalize_work_order(flat)
        structured_work_orders.append(structured)

    tool_logs.append(f"Fetched {len(structured_work_orders)} work orders.")

    # -------------------------------------------------
    # Route to BI Engine
    # -------------------------------------------------

    tool_logs.append("Routing to appropriate BI function...")
    metrics = route_query(parsed, structured_deals, structured_work_orders)

    # -------------------------------------------------
    # Generate Executive Summary
    # -------------------------------------------------

    tool_logs.append("Generating executive summary...")
    summary = generate_executive_summary(parsed, metrics)

    # -------------------------------------------------
    # Display Results
    # -------------------------------------------------

    st.subheader("📌 Executive Summary")
    st.success(summary)

    # -------------------------------------------------
    # Tool Execution Trace
    # -------------------------------------------------

    with st.expander("🔍 Tool Execution Trace"):
        for log in tool_logs:
            st.write(log)

        st.markdown("**Raw Metrics Output:**")
        st.json(metrics)

    