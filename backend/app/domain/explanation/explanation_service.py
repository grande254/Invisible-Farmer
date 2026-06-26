from app.domain.explanation.prompt_templates import build_featherless_review_payload
from app.integrations.featherless.client import FeatherlessClient
from app.integrations.featherless.safe_output import (
    attach_featherless_outputs,
    default_business_explanation,
    sanitize_business_explanation,
)


def generate_business_explanation(decision_support: dict) -> dict:
    try:
        payload = build_featherless_review_payload(decision_support)
        client = FeatherlessClient()

        raw = client.generate_business_explanation(payload)
        return sanitize_business_explanation(raw, decision_support)

    except Exception as exc:
        fallback = default_business_explanation(decision_support, provider="local_fallback")
        fallback["status"] = "fallback"
        fallback["error"] = str(exc)
        fallback["business_use"] = (
            "Fallback explanation used because Featherless was unavailable. "
            "The business output structure remains the same."
        )
        return fallback


def enrich_decision_support_with_explanations(decision_support: dict) -> dict:
    explanation = generate_business_explanation(decision_support)
    return attach_featherless_outputs(decision_support, explanation)