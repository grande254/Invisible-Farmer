from fastapi import APIRouter, HTTPException, Response

from app.domain.audit.demo_evidence_builder import build_demo_evidence_pack
from app.domain.audit.report_builder import (
    build_committee_brief_text,
    build_credit_committee_pack,
    build_farmer_communication_pack,
    build_full_audit_pack,
    build_officer_memo_text,
    build_officer_review_pack,
    build_review_executive_summary,
)
from app.domain.farmer.repository import list_farmers
from app.domain.review.review_orchestrator import create_credit_review
from app.integrations.exports.csv_exporter import (
    PORTFOLIO_CSV_FIELDS,
    build_portfolio_csv_rows,
    rows_to_csv,
)
from app.integrations.masumi.job_store import get_job


router = APIRouter(prefix="/v1/exports", tags=["Exports"])


def text_response(content: str, filename: str) -> Response:
    return Response(
        content=content,
        media_type="text/plain",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


def csv_response(content: str, filename: str) -> Response:
    return Response(
        content=content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.get("/status", operation_id="exports_status")
def exports_status():
    return {
        "status": "ready",
        "business_role": (
            "Exports officer review packs, committee briefs, farmer communication packs, "
            "Masumi audit packs, portfolio CSV, and demo evidence packs."
        ),
        "available_exports": [
            "/v1/exports/review/{farmer_id}/summary",
            "/v1/exports/review/{farmer_id}/officer-pack",
            "/v1/exports/review/{farmer_id}/committee-pack",
            "/v1/exports/review/{farmer_id}/farmer-communication",
            "/v1/exports/review/{farmer_id}/audit-pack",
            "/v1/exports/review/{farmer_id}/officer-memo.txt",
            "/v1/exports/review/{farmer_id}/committee-brief.txt",
            "/v1/exports/portfolio.csv",
            "/v1/exports/masumi-job/{job_id}/audit-pack",
            "/v1/exports/demo-evidence-pack",
        ],
    }


@router.get("/review/{farmer_id}/summary", operation_id="export_review_summary")
def export_review_summary(farmer_id: str):
    try:
        review = create_credit_review(farmer_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return build_review_executive_summary(review)


@router.get("/review/{farmer_id}/officer-pack", operation_id="export_officer_pack")
def export_officer_pack(farmer_id: str):
    try:
        review = create_credit_review(farmer_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return build_officer_review_pack(review)


@router.get("/review/{farmer_id}/committee-pack", operation_id="export_committee_pack")
def export_committee_pack(farmer_id: str):
    try:
        review = create_credit_review(farmer_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return build_credit_committee_pack(review)


@router.get("/review/{farmer_id}/farmer-communication", operation_id="export_farmer_communication")
def export_farmer_communication(farmer_id: str):
    try:
        review = create_credit_review(farmer_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return build_farmer_communication_pack(review)


@router.get("/review/{farmer_id}/audit-pack", operation_id="export_review_audit_pack")
def export_review_audit_pack(farmer_id: str):
    try:
        review = create_credit_review(farmer_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return build_full_audit_pack(review)


@router.get("/review/{farmer_id}/officer-memo.txt", operation_id="export_officer_memo_text")
def export_officer_memo_text(farmer_id: str):
    try:
        review = create_credit_review(farmer_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    content = build_officer_memo_text(review)

    return text_response(
        content=content,
        filename=f"invisible_farmer_{farmer_id}_officer_memo.txt",
    )


@router.get("/review/{farmer_id}/committee-brief.txt", operation_id="export_committee_brief_text")
def export_committee_brief_text(farmer_id: str):
    try:
        review = create_credit_review(farmer_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    content = build_committee_brief_text(review)

    return text_response(
        content=content,
        filename=f"invisible_farmer_{farmer_id}_committee_brief.txt",
    )


@router.get("/portfolio.csv", operation_id="export_portfolio_csv")
def export_portfolio_csv():
    reviews = []

    for farmer in list_farmers():
        try:
            reviews.append(create_credit_review(farmer["farmer_id"]))
        except Exception:
            continue

    rows = build_portfolio_csv_rows(reviews)
    csv_content = rows_to_csv(rows, PORTFOLIO_CSV_FIELDS)

    return csv_response(
        content=csv_content,
        filename="invisible_farmer_portfolio_reviews.csv",
    )


@router.get("/masumi-job/{job_id}/audit-pack", operation_id="export_masumi_job_audit_pack")
def export_masumi_job_audit_pack(job_id: str):
    job = get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail=f"Masumi job {job_id} not found")

    review = job.get("result")

    if not review:
        raise HTTPException(
            status_code=400,
            detail="Masumi job does not have a completed review result yet.",
        )

    return build_full_audit_pack(
        review=review,
        masumi_job=job,
    )


@router.get("/demo-evidence-pack", operation_id="export_demo_evidence_pack")
def export_demo_evidence_pack():
    return build_demo_evidence_pack()