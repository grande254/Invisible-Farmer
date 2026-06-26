import csv
import io


def rows_to_csv(rows: list[dict], fieldnames: list[str]) -> str:
    output = io.StringIO()

    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames,
        extrasaction="ignore",
    )

    writer.writeheader()

    for row in rows:
        writer.writerow(row)

    return output.getvalue()


def build_portfolio_csv_rows(reviews: list[dict]) -> list[dict]:
    rows = []

    for review in reviews:
        decision_support = review.get("decision_support", {})
        credit = decision_support.get("credit_readiness", {})
        graph = decision_support.get("graph_intelligence", {})
        recommendation = decision_support.get("decision_recommendation", {})

        rows.append(
            {
                "review_id": review.get("review_id"),
                "farmer_id": review.get("farmer_id"),
                "farmer_name": review.get("farmer_name"),
                "created_at": review.get("created_at"),
                "score": credit.get("score"),
                "tier": credit.get("tier"),
                "recommended_loan_range": credit.get("recommended_loan_range"),
                "ml_provider": credit.get("provider"),
                "graph_provider": graph.get("provider"),
                "graph_status": graph.get("status"),
                "graph_support_level": graph.get("graph_support_level"),
                "featherless_status": (
                    decision_support.get("featherless_business_explanation", {}).get("status")
                ),
                "recommendation": recommendation.get("recommendation"),
                "loan_officer_final_decision_required": True,
            }
        )

    return rows


PORTFOLIO_CSV_FIELDS = [
    "review_id",
    "farmer_id",
    "farmer_name",
    "created_at",
    "score",
    "tier",
    "recommended_loan_range",
    "ml_provider",
    "graph_provider",
    "graph_status",
    "graph_support_level",
    "featherless_status",
    "recommendation",
    "loan_officer_final_decision_required",
]