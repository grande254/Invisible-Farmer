import re


def slug(value: str) -> str:
    text = str(value or "unknown").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "unknown"


def build_graph_identity(farmer: dict) -> dict:
    county = farmer.get("county", "Unknown")
    area = farmer.get("area", "Unknown")
    crop = farmer.get("crop", "Unknown")

    county_id = f"county_{slug(county)}"
    crop_id = f"crop_{slug(crop)}"

    cooperative_id = f"coop_{slug(county)}_{slug(crop)}"
    cooperative_name = f"{county} {crop} Cooperative"

    savings_group_id = f"sg_{slug(area)}_{slug(crop)}"
    savings_group_name = f"{area} {crop} Savings Group"

    buyer_id = f"buyer_{slug(county)}_{slug(crop)}"
    buyer_name = f"{county} {crop} Buyer Network"

    supplier_id = f"supplier_{slug(county)}_agrovet"
    supplier_name = f"{county} Agrovet Supplier Network"

    extension_id = f"extension_{slug(area)}"
    extension_name = f"{area} Extension Support Desk"

    return {
        "county_id": county_id,
        "crop_id": crop_id,
        "cooperative_id": cooperative_id,
        "cooperative_name": cooperative_name,
        "savings_group_id": savings_group_id,
        "savings_group_name": savings_group_name,
        "buyer_id": buyer_id,
        "buyer_name": buyer_name,
        "supplier_id": supplier_id,
        "supplier_name": supplier_name,
        "extension_id": extension_id,
        "extension_name": extension_name,
    }


def farmer_import_payload(farmer: dict) -> dict:
    payload = {
        "farmer_id": farmer["farmer_id"],
        "name": farmer.get("name"),
        "county": farmer.get("county"),
        "area": farmer.get("area"),
        "crop": farmer.get("crop"),
        "crop_stage": farmer.get("crop_stage"),
        "season": farmer.get("season"),
        "loan_request": farmer.get("loan_request"),
        "loan_purpose": farmer.get("loan_purpose"),
        "farmer_type": farmer.get("farmer_type"),
        "preferred_channel": farmer.get("preferred_channel"),
        "preferred_language": farmer.get("preferred_language"),
        "phone_type": farmer.get("phone_type"),
        "has_land_title": bool(farmer.get("has_land_title")),
        "mobile_money_consistency": farmer.get("mobile_money_consistency"),
        "peer_lending_reliability": farmer.get("peer_lending_reliability"),
        "savings_group_reliability": farmer.get("savings_group_reliability"),
        "cooperative_reliability": farmer.get("cooperative_reliability"),
        "buyer_payment_reliability": farmer.get("buyer_payment_reliability"),
        "market_payment_consistency": farmer.get("market_payment_consistency"),
        "input_purchase_frequency": farmer.get("input_purchase_frequency"),
        "climate_risk_level": farmer.get("climate_risk_level"),
        "pest_risk_level": farmer.get("pest_risk_level"),
        "market_delay_risk": farmer.get("market_delay_risk"),
        "localized_drought_exposure": farmer.get("localized_drought_exposure"),
        "localized_pest_outbreak": farmer.get("localized_pest_outbreak"),
        "cooperative_repayment_score": farmer.get("cooperative_repayment_score"),
        "verified_input_purchase": bool(farmer.get("verified_input_purchase")),
        "extension_support": bool(farmer.get("extension_support")),
        "scenario_label": farmer.get("scenario_label"),
        "primary_graph_signal": farmer.get("primary_graph_signal"),
    }

    payload.update(build_graph_identity(farmer))
    return payload