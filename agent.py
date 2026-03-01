import re
from bi_engine import (
    compute_pipeline_metrics,
    compute_closed_revenue,
    compute_sector_quarter_performance,
    compute_work_order_performance
)



def parse_question(question: str):
    question = question.lower()

    intent = None
    sector = None
    timeframe = None

    # Detect sector (high-level + raw)
    sector_keywords = [
        "mining", "energy", "powerline", "renewables",
        "construction", "railways", "manufacturing"
    ]

    for s in sector_keywords:
        if s in question:
            sector = s
            break

    # Detect timeframe
    if "this quarter" in question:
        timeframe = "this_quarter"
    elif "last quarter" in question:
        timeframe = "last_quarter"

    # Detect intent
    if "pipeline" in question:
        intent = "pipeline"
    elif "revenue" in question:
        intent = "revenue"
    elif "work order" in question:
        intent = "work_order"

    return {
        "intent": intent,
        "sector": sector,
        "timeframe": timeframe
    }

def needs_clarification(parsed):

    if not parsed["intent"]:
        return "Are you asking about pipeline, revenue, or work order performance?"

    if parsed["intent"] == "pipeline" and not parsed["sector"]:
        return "Which sector would you like to analyze?"

    if parsed["intent"] == "pipeline" and not parsed["timeframe"]:
        return "Are you referring to this quarter or another time period?"

    return None



def route_query(parsed, deals, work_orders):

    intent = parsed["intent"]
    sector = parsed["sector"]
    timeframe = parsed["timeframe"]

    # Sector + Quarter Performance
    if intent == "pipeline" and sector and timeframe == "this_quarter":
        return compute_sector_quarter_performance(
            deals,
            work_orders,
            sector
        )

    # Global Pipeline
    if intent == "pipeline" and not sector:
        return compute_pipeline_metrics(deals)

    # Closed Revenue
    if intent == "revenue":
        return compute_closed_revenue(deals)

    # Work Order Global
    if intent == "work_order":
        return compute_work_order_performance(deals, work_orders)

    return {"message": "Unable to interpret query"}

def generate_executive_summary(parsed, metrics):

    if parsed["intent"] == "pipeline" and parsed["sector"]:

        sector = parsed["sector"]
        deals = metrics.get("quarter_deals", 0)
        pipeline = metrics.get("pipeline_value", 0)
        completed = metrics.get("completed_work_orders", 0)
        revenue = metrics.get("completed_revenue", 0)

        return (
            f"{sector.title()} has {deals} deals this quarter "
            f"with a pipeline value of {pipeline:,.2f}. "
            f"{completed} work orders have been completed, "
            f"generating {revenue:,.2f} in revenue."
        )

    if parsed["intent"] == "pipeline":
        return (
            f"There are {metrics['open_deals']} open deals "
            f"with total pipeline value of {metrics['total_pipeline_value']:,.2f} "
            f"and weighted pipeline of {metrics['total_weighted_pipeline']:,.2f}."
        )

    if parsed["intent"] == "revenue":
        return (
            f"{metrics['closed_deals']} deals have closed, "
            f"generating {metrics['total_closed_revenue']:,.2f} in revenue."
        )

    return "Unable to generate executive summary."