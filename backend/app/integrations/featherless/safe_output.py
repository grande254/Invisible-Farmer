from copy import deepcopy


REQUIRED_KEYS = [
    "officer_decision_memo",
    "credit_committee_brief",
    "branch_action_plan",
    "farmer_sms",
    "farmer_ussd_summary",
    "data_collection_checklist",
    "risk_mitigation_notes",
    "inclusion_accessibility_note",
    "audit_explanation",
    "model_limitations",
]


def default_business_explanation(decision_support: dict, provider: str = "local_fallback") -> dict:
    farmer = decision_support["farmer"]
    credit = decision_support["credit_readiness"]
    recommendation = decision_support["decision_recommendation"]
    risk_context = decision_support.get("risk_context", {})

    farmer_name = farmer["name"]
    score = credit.get("score")
    tier = credit.get("tier")
    loan_range = credit.get("recommended_loan_range")
    alternative_data = credit.get("alternative_data_used", [])
    missing_data = credit.get("missing_data", [])
    risk_signals = credit.get("risk_signals", [])
    material_risk_signals = credit.get("material_risk_signals", risk_signals)

    alternative_text = ", ".join(alternative_data[:6]) if alternative_data else "limited alternative evidence"
    missing_text = ", ".join(missing_data[:6]) if missing_data else "no major missing records"
    risk_text = ", ".join(material_risk_signals[:6]) if material_risk_signals else "no material risk signals"

    return {
        "provider": provider,
        "status": "fallback",
        "outputs": {
            "officer_decision_memo": (
                f"{farmer_name} has a {tier} credit-readiness tier with a score of {score}/100. "
                f"The suggested support range is {loan_range}. The review used alternative evidence including "
                f"{alternative_text}. Key missing or verification items: {missing_text}. "
                f"Material risk signals: {risk_text}. This is decision support only; a human loan officer "
                f"must make and record the final outcome."
            ),
            "credit_committee_brief": (
                f"{farmer_name} is assessed as {tier} using ML repayment-readiness scoring and alternative "
                f"farmer evidence. Recommendation: {recommendation.get('recommendation')}. "
                f"Final loan processing depends on human officer review, lender policy, and recorded outcome."
            ),
            "branch_action_plan": [
                "Confirm farmer identity, KYC details, and consent to use alternative evidence.",
                "Verify the strongest alternative evidence used in the review.",
                "Collect missing records listed in the checklist.",
                "Review crop, season, climate, pest, and market context before final officer outcome.",
                "Record the human review outcome before any normal loan processing step.",
            ],
            "farmer_sms": (
                f"Invisible Farmer: Your credit-readiness review is complete. Tier: {tier}. "
                f"Score: {score}/100. Possible support range: {loan_range}. "
                f"Loan officer final decision required."
            ),
            "farmer_ussd_summary": (
                f"Tier: {tier}\n"
                f"Score: {score}/100\n"
                f"Possible support: {loan_range}\n"
                f"Loan officer final decision required."
            ),
            "data_collection_checklist": build_safe_data_collection_checklist(missing_data, credit),
            "risk_mitigation_notes": build_safe_risk_mitigation_notes(
                material_risk_signals=material_risk_signals,
                risk_context=risk_context,
            ),
            "inclusion_accessibility_note": (
                "Protected and inclusion-related fields are used for fairness monitoring, accessibility, "
                "and exclusion-context analysis. They are not used as negative risk penalties. Lack of land "
                "title is treated as collateral-context, not automatic exclusion."
            ),
            "audit_explanation": (
                "The agent generated ML-based credit-readiness decision support using alternative farmer evidence, "
                "reason codes, missing records, fairness context, and risk context. The final lending outcome "
                "remains with the human loan officer."
            ),
            "model_limitations": (
                "The ML model is trained on balanced synthetic repayment data for prototype demonstration. "
                "It should be validated with lender repayment data and monitored for fairness before production use."
            ),
        },
        "quality_controls": {
            "final_decision_made_by_agent": False,
            "loan_officer_final_decision_required": True,
            "safe_for_farmer": True,
            "uses_protected_fields_as_penalty": False,
        },
    }


def ensure_list(value) -> list[str]:
    if value is None:
        return []

    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    if isinstance(value, str):
        lines = [line.strip("-• ").strip() for line in value.split("\n")]
        return [line for line in lines if line]

    return [str(value)]


def clean_risky_language(text: str) -> str:
    replacements = {
        "approved": "ready for further loan officer review",
        "Approved": "Ready for further loan officer review",
        "approval": "loan officer review",
        "Approval": "Loan officer review",
        "rejected": "not ready for normal loan processing",
        "Rejected": "Not ready for normal loan processing",
        "rejection": "manual non-progression outcome",
        "Rejection": "Manual non-progression outcome",
        "guaranteed": "possible",
        "Guaranteed": "Possible",
        "qualifies": "may be considered",
        "Qualifies": "May be considered",
        "will receive": "may be considered for",
        "Will receive": "May be considered for",
        "disbursed": "processed by the lender",
        "Disbursed": "Processed by the lender",
        "automatic approval": "loan officer review",
        "Automatic approval": "Loan officer review",
    }

    cleaned = text or ""

    for risky, safe in replacements.items():
        cleaned = cleaned.replace(risky, safe)

    return cleaned.strip()


def normalize_checklist_item(item: str) -> str:
    text = clean_risky_language(item).strip()
    lower = text.lower()

    if not text:
        return ""

    if "land title" in lower or "formal collateral" in lower or "collateral" in lower:
        return "Document collateral context and apply the lender's alternative-evidence route where available."

    if "formal credit history" in lower:
        return "Check whether any small formal repayment record, SACCO record, or prior lender reference exists."

    if "mobile money" in lower:
        return "Verify mobile money farming transaction evidence where the farmer has consented."

    if "cooperative repayment" in lower or "cooperative" in lower:
        return "Verify cooperative contribution, repayment, or produce delivery records."

    if "peer lending" in lower:
        return "Verify peer lending or savings group reference where available."

    if "market payment" in lower or "buyer" in lower:
        return "Collect buyer receipts, produce sales records, or market payment confirmation."

    if "input purchase" in lower:
        return "Collect input purchase receipts for seed, fertilizer, pesticide, or other farm inputs."

    if "sales records" in lower:
        return "Collect produce sales records showing date, buyer, quantity, and amount."

    if "climate" in lower or "drought" in lower or "pest" in lower:
        return "Record climate, drought, pest, or extension officer mitigation notes."

    return text


def build_safe_data_collection_checklist(missing_data: list[str], credit: dict) -> list[str]:
    checklist = []

    base_items = [
        "Confirm farmer identity, KYC details, and consent to use alternative evidence.",
    ]

    for item in missing_data:
        normalized = normalize_checklist_item(item)

        if normalized and normalized not in checklist:
            checklist.append(normalized)

    if not checklist:
        checklist = [
            "Verify source records behind the strongest alternative evidence before final officer outcome.",
        ]

    return base_items + checklist[:8]


def build_safe_risk_mitigation_notes(
    material_risk_signals: list[str],
    risk_context: dict,
) -> list[str]:
    notes = []

    for signal in material_risk_signals or []:
        lower = signal.lower()

        if "drought" in lower:
            notes.append("Discuss drought timing, water access, irrigation, or crop resilience measures with the farmer.")
        elif "pest" in lower:
            notes.append("Check pest control records, extension support, or input supplier guidance.")
        elif "market delay" in lower:
            notes.append("Check buyer payment timing and whether delayed market payments may affect repayment schedule.")
        elif "missed repayment" in lower:
            notes.append("Review missed repayment context and whether it was seasonal, market-related, or recurring.")
        elif "low" in lower or "none" in lower or "unknown" in lower:
            notes.append(f"Verify weak or missing evidence signal: {signal}.")
        else:
            notes.append(f"Review material risk signal: {signal}.")

    climate = str(risk_context.get("climate_risk_level", "")).lower()
    drought = str(risk_context.get("localized_drought_exposure", "")).lower()
    pest = str(risk_context.get("pest_risk_level", "")).lower()
    market = str(risk_context.get("market_delay_risk", "")).lower()

    if climate == "high" or drought == "high":
        notes.append("Include climate or drought exposure in the repayment timing discussion.")

    if pest == "high":
        notes.append("Ask for pest mitigation evidence or extension officer support before final officer outcome.")

    if market == "high":
        notes.append("Review buyer payment reliability and possible repayment schedule adjustment.")

    if not notes:
        notes.append("No material risk signal is detected from the current review. Continue normal officer verification.")

    deduped = []
    for note in notes:
        if note not in deduped:
            deduped.append(note)

    return deduped[:8]


def sanitize_checklist(raw_items: list[str], decision_support: dict) -> list[str]:
    credit = decision_support["credit_readiness"]
    missing_data = credit.get("missing_data", [])

    cleaned = []

    for item in raw_items:
        normalized = normalize_checklist_item(item)

        if normalized and normalized not in cleaned:
            cleaned.append(normalized)

    required_base = "Confirm farmer identity, KYC details, and consent to use alternative evidence."

    if required_base not in cleaned:
        cleaned.insert(0, required_base)

    if len(cleaned) <= 1:
        cleaned = build_safe_data_collection_checklist(missing_data, credit)

    return cleaned[:9]


def sanitize_risk_notes(raw_items: list[str], decision_support: dict) -> list[str]:
    credit = decision_support["credit_readiness"]
    risk_context = decision_support.get("risk_context", {})
    material_risk_signals = credit.get("material_risk_signals", credit.get("risk_signals", []))

    if not material_risk_signals:
        return build_safe_risk_mitigation_notes([], risk_context)

    cleaned = []

    for item in raw_items:
        text = clean_risky_language(item)
        lower = text.lower()

        # Avoid turning positive evidence into fake risks.
        positive_as_risk = [
            "monitor the farmer's mobile money transactions for consistency",
            "verify the stability of the seasonal income pattern",
            "ensure regular input purchases continue",
            "check market payment consistency regularly",
        ]

        if any(phrase in lower for phrase in positive_as_risk):
            continue

        if text and text not in cleaned:
            cleaned.append(text)

    if not cleaned:
        cleaned = build_safe_risk_mitigation_notes(material_risk_signals, risk_context)

    return cleaned[:8]


def force_farmer_sms_boundary(text: str, decision_support: dict) -> str:
    credit = decision_support["credit_readiness"]
    tier = credit.get("tier", "N/A")
    score = credit.get("score", "N/A")
    loan_range = credit.get("recommended_loan_range", "Not available")

    safe = clean_risky_language(text)

    if "Loan officer final decision required" not in safe:
        safe = f"{safe} Loan officer final decision required."

    if len(safe) > 280:
        safe = (
            f"Invisible Farmer: Review complete. Tier: {tier}. Score: {score}/100. "
            f"Possible support: {loan_range}. Loan officer final decision required."
        )

    return safe


def force_farmer_ussd_boundary(text: str, decision_support: dict) -> str:
    credit = decision_support["credit_readiness"]
    tier = credit.get("tier", "N/A")
    score = credit.get("score", "N/A")
    loan_range = credit.get("recommended_loan_range", "Not available")

    safe = clean_risky_language(text)

    if "Loan officer final decision required" not in safe:
        safe = f"{safe}\nLoan officer final decision required."

    if len(safe) > 180:
        safe = (
            f"Tier: {tier}\n"
            f"Score: {score}/100\n"
            f"Possible support: {loan_range}\n"
            f"Loan officer final decision required."
        )

    return safe


def sanitize_business_explanation(raw: dict, decision_support: dict) -> dict:
    fallback = default_business_explanation(decision_support)
    fallback_outputs = fallback["outputs"]

    raw = raw or {}
    outputs = {}

    for key in REQUIRED_KEYS:
        value = raw.get(key)

        if key in [
            "branch_action_plan",
            "data_collection_checklist",
            "risk_mitigation_notes",
        ]:
            items = ensure_list(value)
            outputs[key] = [
                clean_risky_language(item)
                for item in items
            ] or fallback_outputs[key]
        else:
            outputs[key] = clean_risky_language(str(value)) if value else fallback_outputs[key]

    outputs["data_collection_checklist"] = sanitize_checklist(
        outputs["data_collection_checklist"],
        decision_support,
    )

    outputs["risk_mitigation_notes"] = sanitize_risk_notes(
        outputs["risk_mitigation_notes"],
        decision_support,
    )

    outputs["farmer_sms"] = force_farmer_sms_boundary(outputs["farmer_sms"], decision_support)
    outputs["farmer_ussd_summary"] = force_farmer_ussd_boundary(outputs["farmer_ussd_summary"], decision_support)

    outputs["inclusion_accessibility_note"] = (
        "The system is identity-aware, not identity-scored. Protected and inclusion-related attributes "
        "are used for fairness monitoring, accessibility, and exclusion-context analysis. They are not "
        "used as negative risk penalties. Lack of land title is treated as collateral-context, not "
        "automatic exclusion."
    )

    return {
        "provider": "featherless_ai",
        "status": "live",
        "business_use": (
            "Featherless converts ML score, reason codes, alternative evidence, missing records, "
            "risk context, and fairness context into practical loan officer, branch, committee, "
            "farmer, and audit outputs."
        ),
        "outputs": outputs,
        "quality_controls": {
            "final_decision_made_by_agent": False,
            "loan_officer_final_decision_required": True,
            "safe_for_farmer": True,
            "uses_protected_fields_as_penalty": False,
            "risky_language_sanitized": True,
            "source_of_score": decision_support["credit_readiness"].get("provider"),
        },
    }


def attach_featherless_outputs(decision_support: dict, explanation: dict) -> dict:
    enriched = deepcopy(decision_support)
    outputs = explanation["outputs"]

    enriched["featherless_business_explanation"] = explanation

    enriched["deterministic_officer_memo"] = enriched.get("officer_memo")
    enriched["officer_memo"] = outputs["officer_decision_memo"]

    enriched["credit_committee_brief"] = outputs["credit_committee_brief"]
    enriched["branch_action_plan"] = outputs["branch_action_plan"]
    enriched["data_collection_checklist"] = outputs["data_collection_checklist"]
    enriched["risk_mitigation_notes"] = outputs["risk_mitigation_notes"]
    enriched["inclusion_accessibility_note"] = outputs["inclusion_accessibility_note"]
    enriched["audit_explanation"] = outputs["audit_explanation"]
    enriched["model_limitations"] = outputs["model_limitations"]

    farmer_message = enriched.get("farmer_message", {})
    farmer_message["deterministic_sms"] = farmer_message.get("sms")
    farmer_message["sms"] = outputs["farmer_sms"]
    farmer_message["ai_ussd_summary"] = outputs["farmer_ussd_summary"]
    farmer_message["generated_by"] = explanation["provider"]
    farmer_message["farmer_safe"] = True

    enriched["farmer_message"] = farmer_message

    return enriched