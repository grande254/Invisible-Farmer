import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


RANDOM_SEED = 42
CANDIDATE_ROWS = 30000
FINAL_ROWS = 12000

rng = np.random.default_rng(RANDOM_SEED)

BACKEND_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BACKEND_DIR / "app" / "data" / "synthetic"
OUTPUT_PATH = OUTPUT_DIR / "synthetic_farmer_credit_training.csv"
SUMMARY_PATH = OUTPUT_DIR / "synthetic_data_summary.json"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def choice(options, probs=None):
    return rng.choice(options, p=probs)


def sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


def evidence_score(value, mapping: dict) -> float:
    return mapping.get(value, 0.0)


def generate_one(index: int) -> dict:
    gender = choice(["female", "male"], [0.52, 0.48])

    is_youth = bool(rng.random() < 0.36)
    age = int(rng.integers(18, 35)) if is_youth else int(rng.integers(35, 68))

    is_pwd = bool(rng.random() < 0.11)
    disability_type = None

    if is_pwd:
        disability_type = choice(
            ["mobility", "visual", "hearing", "other"],
            [0.45, 0.20, 0.20, 0.15],
        )

    if is_pwd:
        farmer_type = "PWD farmer"
    elif is_youth:
        farmer_type = "Youth farmer"
    elif gender == "female":
        farmer_type = "Women farmer"
    else:
        farmer_type = "Smallholder farmer"

    county = choice(
        [
            "Kakamega",
            "Kisumu",
            "Nakuru",
            "Bungoma",
            "Machakos",
            "Makueni",
            "Uasin Gishu",
        ],
        [0.18, 0.16, 0.16, 0.13, 0.13, 0.12, 0.12],
    )

    crop = choice(
        ["Maize", "Vegetables", "Potatoes", "Beans", "Sorghum", "Tomatoes"],
        [0.34, 0.18, 0.16, 0.13, 0.10, 0.09],
    )

    season = choice(["long_rains", "short_rains", "dry_season"], [0.48, 0.34, 0.18])
    crop_stage = choice(["planting", "vegetative", "flowering", "harvest"], [0.28, 0.32, 0.22, 0.18])

    # Included for exclusion-context monitoring only.
    # Not used as an ML training feature.
    if gender == "female":
        has_land_title = bool(rng.random() < 0.24)
    elif is_youth:
        has_land_title = bool(rng.random() < 0.18)
    else:
        has_land_title = bool(rng.random() < 0.42)

    phone_type = choice(["feature_phone", "smartphone", "shared_phone"], [0.57, 0.34, 0.09])

    if phone_type in ["feature_phone", "shared_phone"]:
        preferred_channel = "ussd"
    else:
        preferred_channel = choice(["ussd", "sms", "app"], [0.38, 0.28, 0.34])

    preferred_language = choice(["en", "sw"], [0.62, 0.38])
    literacy_level = choice(["low", "medium", "high"], [0.22, 0.58, 0.20])

    base_loan_by_crop = {
        "Maize": 9000,
        "Vegetables": 16000,
        "Potatoes": 15000,
        "Beans": 8000,
        "Sorghum": 7000,
        "Tomatoes": 18000,
    }

    base_loan = base_loan_by_crop[crop]
    loan_request = int(max(3000, rng.normal(base_loan, base_loan * 0.28)))

    mobile_money_consistency = choice(
        ["unknown", "low", "medium", "high"],
        [0.12, 0.22, 0.42, 0.24],
    )

    active_savings_group = bool(rng.random() < 0.70)
    savings_group_reliability = "none"

    if active_savings_group:
        savings_group_reliability = choice(["weak", "medium", "strong"], [0.18, 0.45, 0.37])

    peer_lending_reliability = choice(["none", "weak", "medium", "strong"], [0.18, 0.22, 0.38, 0.22])

    cooperative_member = bool(rng.random() < 0.52)
    cooperative_reliability = "none"
    cooperative_repayment_score = None

    if cooperative_member:
        cooperative_reliability = choice(["weak", "medium", "strong"], [0.18, 0.47, 0.35])
        mean_score = {
            "weak": 45,
            "medium": 67,
            "strong": 84,
        }[cooperative_reliability]
        cooperative_repayment_score = int(np.clip(rng.normal(mean_score, 12), 0, 100))

    reliable_buyer = bool(rng.random() < 0.46)
    buyer_payment_reliability = "none"

    if reliable_buyer:
        buyer_payment_reliability = choice(["weak", "medium", "strong"], [0.20, 0.46, 0.34])

    market_payment_consistency = choice(["none", "weak", "medium", "strong"], [0.20, 0.24, 0.36, 0.20])

    input_purchase_frequency = choice(["none", "low", "medium", "high"], [0.10, 0.28, 0.42, 0.20])
    verified_input_purchase = input_purchase_frequency != "none"

    input_purchase_count = {
        "none": 0,
        "low": int(rng.integers(1, 2)),
        "medium": int(rng.integers(2, 4)),
        "high": int(rng.integers(4, 8)),
    }[input_purchase_frequency]

    completed_repayment_history = bool(rng.random() < 0.54)
    missed_repayment = bool(rng.random() < 0.15)

    has_formal_credit_history = bool(rng.random() < 0.28)
    has_sales_records = bool(rng.random() < 0.48)
    has_buyer_records = reliable_buyer and bool(rng.random() < 0.82)
    extension_support = bool(rng.random() < 0.44)

    seasonal_income_pattern = choice(["unknown", "volatile", "moderate", "stable"], [0.12, 0.25, 0.43, 0.20])

    if county in ["Machakos", "Makueni"]:
        localized_drought_exposure = choice(["low", "medium", "high"], [0.14, 0.34, 0.52])
    elif county in ["Kisumu", "Kakamega", "Bungoma"]:
        localized_drought_exposure = choice(["low", "medium", "high"], [0.35, 0.45, 0.20])
    else:
        localized_drought_exposure = choice(["low", "medium", "high"], [0.28, 0.48, 0.24])

    localized_pest_outbreak = choice(["none", "low", "medium", "high"], [0.24, 0.34, 0.28, 0.14])

    climate_risk_level = localized_drought_exposure

    if localized_pest_outbreak == "high":
        pest_risk_level = "high"
    elif localized_pest_outbreak == "medium":
        pest_risk_level = choice(["medium", "high"], [0.78, 0.22])
    else:
        pest_risk_level = choice(["low", "medium", "high"], [0.42, 0.46, 0.12])

    market_delay_risk = choice(["low", "medium", "high"], [0.34, 0.46, 0.20])

    # Latent repayment-readiness function.
    # Protected/inclusion fields are deliberately NOT used here:
    # gender, age, is_youth, is_pwd, disability_type, farmer_type, has_land_title.
    latent = -0.20

    latent += evidence_score(mobile_money_consistency, {
        "unknown": -0.35,
        "low": -0.10,
        "medium": 0.35,
        "high": 0.75,
    })

    latent += evidence_score(savings_group_reliability, {
        "none": -0.35,
        "weak": 0.05,
        "medium": 0.35,
        "strong": 0.70,
    })

    latent += evidence_score(peer_lending_reliability, {
        "none": -0.25,
        "weak": 0.05,
        "medium": 0.30,
        "strong": 0.60,
    })

    latent += evidence_score(cooperative_reliability, {
        "none": -0.20,
        "weak": 0.05,
        "medium": 0.30,
        "strong": 0.60,
    })

    if cooperative_repayment_score is not None:
        latent += (cooperative_repayment_score - 55) / 80

    latent += evidence_score(buyer_payment_reliability, {
        "none": -0.25,
        "weak": 0.05,
        "medium": 0.35,
        "strong": 0.70,
    })

    latent += evidence_score(market_payment_consistency, {
        "none": -0.35,
        "weak": 0.00,
        "medium": 0.35,
        "strong": 0.70,
    })

    latent += evidence_score(input_purchase_frequency, {
        "none": -0.30,
        "low": 0.05,
        "medium": 0.35,
        "high": 0.70,
    })

    latent += evidence_score(seasonal_income_pattern, {
        "unknown": -0.15,
        "volatile": -0.45,
        "moderate": 0.20,
        "stable": 0.55,
    })

    if completed_repayment_history:
        latent += 0.75

    if missed_repayment:
        latent -= 1.00

    if has_sales_records:
        latent += 0.35
    else:
        latent -= 0.25

    if has_buyer_records:
        latent += 0.25

    if has_formal_credit_history:
        latent += 0.15

    if extension_support:
        latent += 0.20

    latent += evidence_score(localized_drought_exposure, {
        "low": 0.15,
        "medium": -0.25,
        "high": -0.75,
    })

    latent += evidence_score(localized_pest_outbreak, {
        "none": 0.15,
        "low": -0.05,
        "medium": -0.35,
        "high": -0.70,
    })

    latent += evidence_score(market_delay_risk, {
        "low": 0.15,
        "medium": -0.25,
        "high": -0.55,
    })

    if loan_request > base_loan * 1.35:
        latent -= 0.25

    latent += rng.normal(0, 0.60)

    repayment_probability = sigmoid(latent)
    target_repaid_on_time = int(rng.random() < repayment_probability)

    if target_repaid_on_time:
        repayment_outcome = choice(["on_time", "early", "fully_repaid"], [0.58, 0.15, 0.27])
    else:
        repayment_outcome = choice(["late", "restructured", "defaulted"], [0.46, 0.28, 0.26])

    return {
        "farmer_id": f"SYN-{index:05d}",

        "gender": gender,
        "age": age,
        "is_youth": is_youth,
        "is_pwd": is_pwd,
        "disability_type": disability_type,
        "farmer_type": farmer_type,
        "has_land_title": has_land_title,

        "county": county,
        "crop": crop,
        "crop_stage": crop_stage,
        "season": season,
        "phone_type": phone_type,
        "preferred_channel": preferred_channel,
        "preferred_language": preferred_language,
        "literacy_level": literacy_level,

        "loan_request": loan_request,
        "completed_repayment_history": completed_repayment_history,
        "missed_repayment": missed_repayment,
        "has_formal_credit_history": has_formal_credit_history,
        "has_sales_records": has_sales_records,
        "has_buyer_records": has_buyer_records,

        "active_savings_group": active_savings_group,
        "savings_group_reliability": savings_group_reliability,

        "cooperative_member": cooperative_member,
        "cooperative_reliability": cooperative_reliability,
        "cooperative_repayment_score": cooperative_repayment_score,

        "reliable_buyer": reliable_buyer,
        "buyer_payment_reliability": buyer_payment_reliability,

        "verified_input_purchase": verified_input_purchase,
        "input_purchase_count": input_purchase_count,
        "input_purchase_frequency": input_purchase_frequency,

        "extension_support": extension_support,

        "mobile_money_consistency": mobile_money_consistency,
        "peer_lending_reliability": peer_lending_reliability,
        "seasonal_income_pattern": seasonal_income_pattern,
        "market_payment_consistency": market_payment_consistency,

        "climate_risk_level": climate_risk_level,
        "pest_risk_level": pest_risk_level,
        "market_delay_risk": market_delay_risk,
        "localized_pest_outbreak": localized_pest_outbreak,
        "localized_drought_exposure": localized_drought_exposure,

        "latent_repayment_probability": round(repayment_probability, 4),
        "repayment_outcome": repayment_outcome,
        "target_repaid_on_time": target_repaid_on_time,
    }


def build_balanced_dataset() -> pd.DataFrame:
    rows = [generate_one(i) for i in range(CANDIDATE_ROWS)]
    df = pd.DataFrame(rows)

    positive = df[df["target_repaid_on_time"] == 1]
    negative = df[df["target_repaid_on_time"] == 0]

    n_each = min(len(positive), len(negative), FINAL_ROWS // 2)

    balanced = pd.concat(
        [
            positive.sample(n=n_each, random_state=RANDOM_SEED),
            negative.sample(n=n_each, random_state=RANDOM_SEED),
        ]
    )

    balanced = balanced.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)

    return balanced


def main():
    df = build_balanced_dataset()
    df.to_csv(OUTPUT_PATH, index=False)

    summary = {
        "rows": int(len(df)),
        "target_distribution": {
            str(k): int(v)
            for k, v in df["target_repaid_on_time"].value_counts().to_dict().items()
        },
        "repayment_outcomes": {
            str(k): int(v)
            for k, v in df["repayment_outcome"].value_counts().to_dict().items()
        },
        "gender_distribution": {
            str(k): int(v)
            for k, v in df["gender"].value_counts().to_dict().items()
        },
        "youth_distribution": {
            str(k): int(v)
            for k, v in df["is_youth"].value_counts().to_dict().items()
        },
        "pwd_distribution": {
            str(k): int(v)
            for k, v in df["is_pwd"].value_counts().to_dict().items()
        },
        "note": (
            "Synthetic repayment labels are generated from alternative farmer evidence. "
            "Protected and inclusion-related fields are included for fairness monitoring "
            "and accessibility context but are not used in the latent repayment function."
        ),
    }

    SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("Synthetic training data created.")
    print(f"CSV: {OUTPUT_PATH}")
    print(f"Summary: {SUMMARY_PATH}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()