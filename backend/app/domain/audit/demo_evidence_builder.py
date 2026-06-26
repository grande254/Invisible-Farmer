from app.domain.audit.report_builder import now_iso


def build_demo_evidence_pack() -> dict:
    return {
        "pack_type": "demo_evidence_pack",
        "generated_at": now_iso(),
        "project": "Invisible Farmer Credit Review Agent",
        "agent_version": "v2",
        "business_problem": (
            "Rural loan officers struggle to review thin-file smallholder farmers because useful "
            "alternative credit evidence is scattered across mobile money, cooperatives, savings groups, "
            "buyers, input suppliers, and extension support."
        ),
        "business_user": "Rural SACCO, MFI, cooperative, or agri-finance loan officer",
        "workflow": [
            "Loan officer starts farmer credit-readiness review.",
            "Masumi creates job and audit record.",
            "ML Scoring Agent predicts repayment readiness.",
            "Neo4j Graph Intelligence identifies relationship verification paths.",
            "Featherless Business Explanation Agent generates practical business outputs.",
            "Farmer receives safe SMS/USSD guidance.",
            "Human loan officer records final outcome.",
        ],
        "live_modules": {
            "ml_scoring_agent": {
                "status": "live",
                "business_value": "Predicts repayment readiness using alternative farmer evidence.",
            },
            "featherless_business_explanation_agent": {
                "status": "live",
                "business_value": (
                    "Turns score, reason codes, graph evidence, and missing data into officer memo, "
                    "committee brief, branch action plan, farmer SMS/USSD, checklist, risk notes, and audit explanation."
                ),
            },
            "neo4j_graph_intelligence_agent": {
                "status": "live_or_fallback_depending_on_setup",
                "business_value": (
                    "Reveals hidden relationship evidence across cooperative, savings group, buyer, "
                    "input supplier, extension officer, crop, county, and peer profile connections."
                ),
            },
            "masumi_job_audit_agent": {
                "status": "local_live",
                "business_value": (
                    "Records job request, payment status, review output, audit events, and human outcome."
                ),
            },
            "farmer_ussd_agent": {
                "status": "live",
                "business_value": "Gives farmers safe review status and improvement guidance by USSD.",
            },
            "officer_branch_ussd_agent": {
                "status": "live",
                "business_value": (
                    "Lets rural loan officers start reviews, check summaries, copy farmer messages, "
                    "check Masumi job status, and record outcomes from low-bandwidth branch USSD."
                ),
            },
        },
        "responsible_ai_boundary": {
            "agent_approves_or_rejects_loans": False,
            "agent_disburses_money": False,
            "human_loan_officer_final_decision_required": True,
            "allowed_human_outcomes": [
                "Proceed to loan processing",
                "Request more information",
                "Adjust recommended amount",
                "Defer for record building",
                "Manual decline",
            ],
        },
        "demo_sequence": [
            "GET /availability",
            "POST /start_job with F001",
            "GET /v1/masumi/jobs/{job_id}",
            "POST /v1/reviews/F001",
            "POST /v1/graph/F001",
            "POST /v1/explanations/F001",
            "POST /v1/ussd/simulate with text 1*F001",
            "POST /v1/officer-ussd/simulate with text 1234*2*F001",
            "POST /v1/masumi/jobs/{job_id}/human-outcome",
            "GET /v1/exports/review/F001/audit-pack",
        ],
        "judging_note": (
            "The system is business-first. The agent solves a real lender workflow problem by packaging "
            "thin-file farmer evidence into reviewable, explainable, auditable decision support."
        ),
    }