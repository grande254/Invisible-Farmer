from datetime import datetime, timezone


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_get(data: dict, path: list[str], default=None):
    current = data

    for key in path:
        if not isinstance(current, dict):
            return default

        current = current.get(key)

        if current is None:
            return default

    return current


def build_review_executive_summary(review: dict) -> dict:
    decision_support = review.get("decision_support", {})
    credit = decision_support.get("credit_readiness", {})
    graph = decision_support.get("graph_intelligence", {})
    explanation = decision_support.get("featherless_business_explanation", {})
    recommendation = decision_support.get("decision_recommendation", {})

    return {
        "review_id": review.get("review_id"),
        "farmer_id": review.get("farmer_id"),
        "farmer_name": review.get("farmer_name"),
        "created_at": review.get("created_at"),
        "review_type": review.get("review_type"),
        "status": review.get("status"),
        "score": credit.get("score"),
        "tier": credit.get("tier"),
        "recommended_loan_range": credit.get("recommended_loan_range"),
        "ml_provider": credit.get("provider"),
        "ml_model_version": credit.get("model_version"),
        "graph_provider": graph.get("provider"),
        "graph_status": graph.get("status"),
        "graph_support_level": graph.get("graph_support_level"),
        "featherless_provider": explanation.get("provider"),
        "featherless_status": explanation.get("status"),
        "recommendation": recommendation.get("recommendation"),
        "loan_officer_final_decision_required": True,
        "not_an_approval": True,
        "not_a_rejection": True,
    }


def build_officer_review_pack(review: dict) -> dict:
    decision_support = review.get("decision_support", {})
    farmer = decision_support.get("farmer", {})
    credit = decision_support.get("credit_readiness", {})
    graph = decision_support.get("graph_intelligence", {})
    recommendation = decision_support.get("decision_recommendation", {})

    return {
        "pack_type": "loan_officer_review_pack",
        "generated_at": now_iso(),
        "executive_summary": build_review_executive_summary(review),
        "farmer": farmer,
        "credit_readiness": {
            "score": credit.get("score"),
            "tier": credit.get("tier"),
            "repayment_readiness_probability": credit.get("repayment_readiness_probability"),
            "recommended_loan_range": credit.get("recommended_loan_range"),
            "confidence": credit.get("confidence"),
            "positive_signals": credit.get("positive_signals", []),
            "risk_signals": credit.get("risk_signals", []),
            "technical_risk_signals": credit.get("technical_risk_signals", []),
            "missing_data": credit.get("missing_data", []),
            "alternative_data_used": credit.get("alternative_data_used", []),
            "model_reason_codes": credit.get("model_reason_codes", {}),
        },
        "graph_intelligence": {
            "provider": graph.get("provider"),
            "status": graph.get("status"),
            "graph_support_level": graph.get("graph_support_level"),
            "graph_summary": graph.get("graph_summary"),
            "trusted_relationship_signals": graph.get("trusted_relationship_signals", []),
            "network_risk_signals": graph.get("network_risk_signals", []),
            "relationship_paths": graph.get("relationship_paths", []),
            "recommended_verification_path": graph.get("recommended_verification_path", []),
            "similarity_evidence": graph.get("similarity_evidence", []),
        },
        "decision_recommendation": recommendation,
        "officer_memo": decision_support.get("officer_memo"),
        "credit_committee_brief": decision_support.get("credit_committee_brief"),
        "branch_action_plan": decision_support.get("branch_action_plan", []),
        "data_collection_checklist": decision_support.get("data_collection_checklist", []),
        "risk_mitigation_notes": decision_support.get("risk_mitigation_notes", []),
        "farmer_message": decision_support.get("farmer_message", {}),
        "responsible_ai_boundary": review.get("responsible_ai_boundary"),
    }


def build_credit_committee_pack(review: dict) -> dict:
    decision_support = review.get("decision_support", {})
    credit = decision_support.get("credit_readiness", {})
    graph = decision_support.get("graph_intelligence", {})

    return {
        "pack_type": "credit_committee_pack",
        "generated_at": now_iso(),
        "executive_summary": build_review_executive_summary(review),
        "committee_brief": decision_support.get("credit_committee_brief"),
        "scorecard_snapshot": {
            "provider": credit.get("provider"),
            "model_type": credit.get("model_type"),
            "model_version": credit.get("model_version"),
            "score": credit.get("score"),
            "tier": credit.get("tier"),
            "recommended_loan_range": credit.get("recommended_loan_range"),
            "confidence": credit.get("confidence"),
        },
        "relationship_evidence_snapshot": {
            "provider": graph.get("provider"),
            "status": graph.get("status"),
            "graph_support_level": graph.get("graph_support_level"),
            "trusted_relationship_signals": graph.get("trusted_relationship_signals", []),
            "network_risk_signals": graph.get("network_risk_signals", []),
        },
        "human_review_options": safe_get(
            decision_support,
            ["decision_recommendation", "human_review_options"],
            [],
        ),
        "important_boundary": (
            "This pack supports credit committee and loan officer review. "
            "It is not an autonomous approval, rejection, or disbursement decision."
        ),
    }


def build_farmer_communication_pack(review: dict) -> dict:
    decision_support = review.get("decision_support", {})
    farmer_message = decision_support.get("farmer_message", {})

    return {
        "pack_type": "farmer_communication_pack",
        "generated_at": now_iso(),
        "review_id": review.get("review_id"),
        "farmer_id": review.get("farmer_id"),
        "farmer_name": review.get("farmer_name"),
        "sms": farmer_message.get("sms"),
        "ussd_summary": farmer_message.get("ai_ussd_summary"),
        "deterministic_sms": farmer_message.get("deterministic_sms"),
        "improvement_tips": farmer_message.get("improvement_tips", []),
        "farmer_safe": farmer_message.get("farmer_safe", True),
        "generated_by": farmer_message.get("generated_by"),
        "important_boundary": "Farmer-facing messages do not approve or reject loans.",
    }


def build_full_audit_pack(review: dict, masumi_job: dict | None = None) -> dict:
    decision_support = review.get("decision_support", {})

    return {
        "pack_type": "full_audit_pack",
        "generated_at": now_iso(),
        "review": {
            "executive_summary": build_review_executive_summary(review),
            "module_status": review.get("module_status"),
            "responsible_ai_boundary": review.get("responsible_ai_boundary"),
        },
        "loan_officer_pack": build_officer_review_pack(review),
        "credit_committee_pack": build_credit_committee_pack(review),
        "farmer_communication_pack": build_farmer_communication_pack(review),
        "fairness": decision_support.get("fairness", {}),
        "inclusion_context": decision_support.get("inclusion_context", {}),
        "audit_explanation": decision_support.get("audit_explanation"),
        "model_limitations": decision_support.get("model_limitations"),
        "masumi_job": masumi_job,
        "audit_boundary": (
            "The audit pack records how the agent produced decision support. "
            "It does not represent final credit approval or rejection."
        ),
    }


def render_text_report(title: str, sections: list[tuple[str, str | list]]) -> str:
    lines = [
        title,
        "=" * len(title),
        "",
        f"Generated at: {now_iso()}",
        "",
    ]

    for heading, content in sections:
        lines.append(heading)
        lines.append("-" * len(heading))

        if isinstance(content, list):
            if not content:
                lines.append("None")
            else:
                for item in content:
                    lines.append(f"- {item}")
        else:
            lines.append(str(content or "Not available"))

        lines.append("")

    return "\n".join(lines)


def build_officer_memo_text(review: dict) -> str:
    decision_support = review.get("decision_support", {})
    credit = decision_support.get("credit_readiness", {})
    graph = decision_support.get("graph_intelligence", {})
    recommendation = decision_support.get("decision_recommendation", {})

    return render_text_report(
        title="Invisible Farmer Loan Officer Review Memo",
        sections=[
            ("Review ID", review.get("review_id")),
            ("Farmer", f"{review.get('farmer_name')} ({review.get('farmer_id')})"),
            ("Score", f"{credit.get('score')}/100"),
            ("Tier", credit.get("tier")),
            ("Suggested Support Range", credit.get("recommended_loan_range")),
            ("ML Provider", credit.get("provider")),
            ("Graph Provider", graph.get("provider")),
            ("Graph Support Level", graph.get("graph_support_level")),
            ("Recommendation", recommendation.get("recommendation")),
            ("Reason", recommendation.get("reason")),
            ("Officer Memo", decision_support.get("officer_memo")),
            ("Verification Path", graph.get("recommended_verification_path", [])),
            ("Data Collection Checklist", decision_support.get("data_collection_checklist", [])),
            ("Boundary", "Human loan officer final decision required. This is not an approval or rejection."),
        ],
    )


def build_committee_brief_text(review: dict) -> str:
    decision_support = review.get("decision_support", {})
    credit = decision_support.get("credit_readiness", {})
    graph = decision_support.get("graph_intelligence", {})

    return render_text_report(
        title="Invisible Farmer Credit Committee Brief",
        sections=[
            ("Review ID", review.get("review_id")),
            ("Farmer", f"{review.get('farmer_name')} ({review.get('farmer_id')})"),
            ("Score and Tier", f"{credit.get('score')}/100 — {credit.get('tier')}"),
            ("Support Range", credit.get("recommended_loan_range")),
            ("Committee Brief", decision_support.get("credit_committee_brief")),
            ("Graph Intelligence", graph.get("graph_summary")),
            ("Risk Mitigation Notes", decision_support.get("risk_mitigation_notes", [])),
            ("Model Limitations", decision_support.get("model_limitations")),
            ("Boundary", "Committee review remains subject to human decision and lender policy."),
        ],
    )