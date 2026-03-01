from collections import defaultdict
from datetime import datetime


# =====================================================
# 1️⃣ BUSINESS TAXONOMY (Sector Aggregation Layer)
# =====================================================

SECTOR_GROUPS = {
    "energy": ["powerline", "renewables"],
    "infrastructure": ["construction", "railways"],
    "industrial": ["manufacturing", "dsp"],
    "defense": ["security and surveillance"],
}


def expand_sector(sector):
    """
    Expands high-level business sector
    into underlying CRM sector values.
    """
    if not sector:
        return []

    sector = sector.lower()

    if sector in SECTOR_GROUPS:
        return SECTOR_GROUPS[sector]

    return [sector]


def get_available_sectors(deals):
    return sorted({
        d.get("sector")
        for d in deals
        if d.get("sector")
    })


# =====================================================
# 2️⃣ STATUS HELPERS
# =====================================================

def is_open(deal):
    return deal.get("deal_status", "").lower() == "open"


def is_closed_won(deal):
    status = deal.get("deal_status", "")
    return "won" in status.lower()


# =====================================================
# 3️⃣ CORE DEAL METRICS
# =====================================================

def compute_pipeline_metrics(deals):
    total_pipeline = 0
    total_weighted = 0
    open_deals_count = 0

    for deal in deals:
        if is_open(deal):
            open_deals_count += 1

            if deal.get("deal_value"):
                total_pipeline += deal["deal_value"]

            if deal.get("weighted_value"):
                total_weighted += deal["weighted_value"]

    return {
        "open_deals": open_deals_count,
        "total_pipeline_value": total_pipeline,
        "total_weighted_pipeline": total_weighted
    }


def compute_closed_revenue(deals):
    total_revenue = 0
    closed_count = 0

    for deal in deals:
        if is_closed_won(deal):
            closed_count += 1
            if deal.get("deal_value"):
                total_revenue += deal["deal_value"]

    return {
        "closed_deals": closed_count,
        "total_closed_revenue": total_revenue
    }


def compute_sector_breakdown(deals):
    sector_totals = defaultdict(float)

    for deal in deals:
        sector = deal.get("sector")
        value = deal.get("deal_value")

        if sector and value:
            sector_totals[sector] += value

    return dict(sector_totals)


# =====================================================
# 4️⃣ FILTER HELPERS
# =====================================================

def filter_by_sector(deals, sector):
    return [
        d for d in deals
        if d.get("sector") and d["sector"] == sector.lower()
    ]


def filter_this_quarter(deals):
    now = datetime.now()
    current_quarter = (now.month - 1) // 3 + 1
    current_year = now.year

    filtered = []

    for deal in deals:
        date = deal.get("tentative_close_date") or deal.get("created_date")

        if not date:
            continue

        deal_quarter = (date.month - 1) // 3 + 1

        if date.year == current_year and deal_quarter == current_quarter:
            filtered.append(deal)

    return filtered


# =====================================================
# 5️⃣ CROSS-BOARD WORK ORDER METRICS
# =====================================================

def compute_work_order_performance(deals, work_orders):
    """
    Join deals and work orders using normalized client_code
    and compute fulfillment metrics.
    """

    deal_clients = {
        d.get("client_code")
        for d in deals
        if d.get("client_code")
    }

    related_work_orders = [
        wo for wo in work_orders
        if wo.get("client_code") in deal_clients
    ]

    completed_work_orders = []

    for wo in related_work_orders:
        status = wo.get("work_order_status")

        if status and status.lower() == "completed":
            completed_work_orders.append(wo)

    total_completed_revenue = sum(
        wo.get("revenue", 0)
        for wo in completed_work_orders
        if wo.get("revenue")
    )

    return {
        "total_related_work_orders": len(related_work_orders),
        "completed_work_orders": len(completed_work_orders),
        "completed_work_order_revenue": total_completed_revenue
    }


# =====================================================
# 6️⃣ SECTOR + QUARTER CROSS-BOARD PERFORMANCE
# =====================================================

def compute_sector_quarter_performance(deals, work_orders, sector):

    # Expand high-level sector
    expanded_sectors = expand_sector(sector)

    # Filter deals by sector
    filtered_deals = [
        d for d in deals
        if d.get("sector") in expanded_sectors
    ]

    # Current quarter calculation
    now = datetime.now()
    current_quarter = (now.month - 1) // 3 + 1
    current_year = now.year

    quarter_deals = []

    for d in filtered_deals:
        date = d.get("tentative_close_date") or d.get("created_date")

        if not date:
            continue

        deal_quarter = (date.month - 1) // 3 + 1

        if date.year == current_year and deal_quarter == current_quarter:
            quarter_deals.append(d)

    total_pipeline = sum(
        d.get("deal_value", 0)
        for d in quarter_deals
        if d.get("deal_value")
    )

    deal_clients = {
        d.get("client_code")
        for d in quarter_deals
        if d.get("client_code")
    }

    related_work_orders = [
        wo for wo in work_orders
        if wo.get("client_code") in deal_clients
    ]

    completed = [
        wo for wo in related_work_orders
        if wo.get("work_order_status")
        and wo["work_order_status"].lower() == "completed"
    ]

    completed_revenue = sum(
        wo.get("revenue", 0)
        for wo in completed
        if wo.get("revenue")
    )

    return {
        "sector": sector,
        "quarter_deals": len(quarter_deals),
        "pipeline_value": total_pipeline,
        "completed_work_orders": len(completed),
        "completed_revenue": completed_revenue
    }