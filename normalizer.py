import json
from datetime import datetime


# =====================================================
# 1️⃣ SAFE TYPE CONVERSIONS & HELPERS
# =====================================================

def parse_json_value(value):
    if not value:
        return None
    try:
        return json.loads(value)
    except:
        return value


def safe_float(value):
    if not value:
        return None
    try:
        return float(str(value).replace(",", "").replace("$", ""))
    except:
        return None


def safe_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except:
        return None


def normalize_client_code(code):
    if not code:
        return None

    code = code.upper()
    code = code.replace("WOCOMPANY_", "")
    code = code.replace("COMPANY", "")
    return code.strip()


def map_probability(label):
    if not label:
        return None

    label = label.lower()

    if "high" in label:
        return 0.8
    if "medium" in label:
        return 0.5
    if "low" in label:
        return 0.2

    return None


# =====================================================
# 2️⃣ FLATTEN RAW MONDAY ITEM
# =====================================================

def normalize_item(raw_item):
    """
    Converts Monday nested column_values structure
    into flat dictionary using column IDs.
    """
    normalized = {}

    normalized["item_id"] = raw_item.get("id")
    normalized["item_name"] = raw_item.get("name")

    for col in raw_item.get("column_values", []):
        col_id = col.get("id")
        text = col.get("text")
        raw_value = parse_json_value(col.get("value"))

        normalized[col_id] = text if text else raw_value

    return normalized


# =====================================================
# 3️⃣ COLUMN MAPPINGS
# =====================================================

COLUMN_MAP_DEALS = {
    "color_mm10h88a": "owner_code",
    "text_mm10xkec": "client_code",
    "color_mm10bmnw": "deal_status",
    "date_mm108x44": "close_date_actual",
    "color_mm10c2r6": "closure_probability",
    "numeric_mm10k0np": "deal_value",
    "date_mm10azbk": "tentative_close_date",
    "color_mm1047dg": "deal_stage",
    "color_mm10yj9f": "product_deal",
    "color_mm1043dq": "sector",
    "date_mm1068jn": "created_date",
}

COLUMN_MAP_WORK_ORDERS = {
    "text_mm1047hk": "client_code",
    "color_mm106msh": "work_order_status",
    "color_mm108yya": "sector",
    "numeric_mm106xrn": "revenue",
    "date_mm10ny7d": "created_date",
    "date_mm105v6n": "completion_date"
}


# =====================================================
# 4️⃣ DEAL NORMALIZATION
# =====================================================

def normalize_deal(flat_item):
    """
    Converts flattened item into structured,
    analytics-ready Deal object.
    """

    structured = {
        "deal_id": flat_item.get("item_id"),
        "deal_name": flat_item.get("item_name")
    }

    for col_id, semantic_name in COLUMN_MAP_DEALS.items():
        value = flat_item.get(col_id)

        if semantic_name == "deal_value":
            structured["deal_value"] = safe_float(value)

        elif "date" in semantic_name:
            structured[semantic_name] = safe_date(value)

        elif semantic_name == "sector":
            structured["sector"] = value.lower().strip() if value else None

        elif semantic_name == "client_code":
            structured["client_code"] = normalize_client_code(value)

        else:
            structured[semantic_name] = value

    # Probability mapping
    structured["probability"] = map_probability(
        structured.get("closure_probability")
    )

    # Weighted pipeline calculation
    if structured.get("deal_value") and structured.get("probability"):
        structured["weighted_value"] = (
            structured["deal_value"] * structured["probability"]
        )
    else:
        structured["weighted_value"] = None

    return structured


# =====================================================
# 5️⃣ WORK ORDER NORMALIZATION
# =====================================================

def normalize_work_order(flat_item):

    structured = {
        "work_order_id": flat_item.get("item_id"),
        "work_order_name": flat_item.get("item_name")
    }

    for col_id, semantic_name in COLUMN_MAP_WORK_ORDERS.items():
        value = flat_item.get(col_id)

        if semantic_name == "revenue":
            structured["revenue"] = safe_float(value)

        elif "date" in semantic_name:
            structured[semantic_name] = safe_date(value)

        elif semantic_name == "sector":
            structured["sector"] = value.lower().strip() if value else None

        elif semantic_name == "client_code":
            structured["client_code"] = normalize_client_code(value)

        else:
            structured[semantic_name] = value

    return structured