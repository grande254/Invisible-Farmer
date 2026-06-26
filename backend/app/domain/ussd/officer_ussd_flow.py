from app.agents.masumi_job_agent import ALLOWED_HUMAN_OUTCOMES, masumi_job_agent
from app.domain.farmer.repository import get_farmer_by_id
from app.domain.review.review_orchestrator import create_credit_review
from app.domain.ussd.ussd_screen_builder import compact, con, end, parse_ussd_path


OFFICER_PIN = "1234"


def officer_main_menu() -> dict:
    return con(
        "Officer Branch USSD\n"
        "1. Start farmer review\n"
        "2. Check compact summary\n"
        "3. Record human outcome\n"
        "4. Copy farmer SMS\n"
        "5. Masumi job status\n"
        "0. Exit"
    )


def ask_pin() -> dict:
    return con("Enter officer PIN:")


def invalid_pin() -> dict:
    return end("Invalid officer PIN. Access denied.")


def ask_farmer_id(label: str) -> dict:
    return con(label)


def require_job_id() -> dict:
    return con("Enter Masumi Job ID:")


def start_farmer_review(farmer_id: str) -> dict:
    farmer = get_farmer_by_id(farmer_id)

    if not farmer:
        return end("Farmer not found. Confirm Farmer ID.")

    job = masumi_job_agent.start_job(
        farmer_id=farmer_id,
        requested_by="Officer Branch USSD",
        purpose="USSD branch credit-readiness review",
    )

    return end(
        compact(
            f"Review created.\n"
            f"Job: {job['job_id']}\n"
            f"Status: {job['status']}\n"
            f"Payment: {job['payment_status']}",
            180,
        )
    )


def compact_summary(farmer_id: str) -> dict:
    farmer = get_farmer_by_id(farmer_id)

    if not farmer:
        return end("Farmer not found. Confirm Farmer ID.")

    review = create_credit_review(farmer_id)
    ds = review["decision_support"]
    credit = ds["credit_readiness"]
    graph = ds.get("graph_intelligence", {})
    recommendation = ds["decision_recommendation"]

    text = (
        f"{farmer['name']} {farmer['farmer_id']}\n"
        f"Score: {credit.get('score')}/100 {credit.get('tier')}\n"
        f"Range: {credit.get('recommended_loan_range')}\n"
        f"Graph: {graph.get('graph_support_level', 'N/A')}\n"
        f"{recommendation.get('recommendation')}\n"
        f"Officer final decision required."
    )

    return end(compact(text, 220))


def human_outcome_menu(job_id: str) -> dict:
    options = "\n".join(
        [f"{index + 1}. {outcome}" for index, outcome in enumerate(ALLOWED_HUMAN_OUTCOMES)]
    )

    return con(
        f"Job: {job_id}\n"
        f"Select human outcome:\n"
        f"{options}"
    )


def record_human_outcome(job_id: str, option: str) -> dict:
    try:
        index = int(option) - 1
    except ValueError:
        return end("Invalid outcome option.")

    if index < 0 or index >= len(ALLOWED_HUMAN_OUTCOMES):
        return end("Invalid outcome option.")

    outcome = ALLOWED_HUMAN_OUTCOMES[index]

    try:
        result = masumi_job_agent.record_human_outcome(
            job_id=job_id,
            outcome=outcome,
            officer_name="Officer Branch USSD",
            notes="Outcome recorded through branch USSD mode.",
        )
    except ValueError as exc:
        return end(str(exc))

    return end(
        compact(
            f"Human outcome recorded.\n"
            f"Job: {job_id}\n"
            f"Outcome: {result['human_review_outcome']['outcome']}\n"
            f"Not AI approval/rejection.",
            200,
        )
    )


def copy_farmer_sms(farmer_id: str) -> dict:
    farmer = get_farmer_by_id(farmer_id)

    if not farmer:
        return end("Farmer not found. Confirm Farmer ID.")

    review = create_credit_review(farmer_id)
    sms = review["decision_support"]["farmer_message"]["sms"]

    return end(compact(sms, 220))


def masumi_job_status(job_id: str) -> dict:
    try:
        status = masumi_job_agent.get_status(job_id)
    except ValueError as exc:
        return end(str(exc))

    payment = status.get("payment") or {}

    return end(
        compact(
            f"Job: {job_id}\n"
            f"Status: {status.get('status')}\n"
            f"Payment: {payment.get('payment_status')}\n"
            f"Human outcome: {status.get('human_review_outcome') is not None}",
            200,
        )
    )


def handle_officer_ussd(text: str | None, phone_number: str | None = None) -> dict:
    path = parse_ussd_path(text)

    if not path:
        return ask_pin()

    pin = path[0]

    if pin != OFFICER_PIN:
        return invalid_pin()

    if len(path) == 1:
        return officer_main_menu()

    option = path[1]

    if option == "0":
        return end("Officer session closed.")

    if option == "1":
        if len(path) == 2:
            return ask_farmer_id("Enter Farmer ID to start review:")

        return start_farmer_review(path[2])

    if option == "2":
        if len(path) == 2:
            return ask_farmer_id("Enter Farmer ID for compact summary:")

        return compact_summary(path[2])

    if option == "3":
        if len(path) == 2:
            return require_job_id()

        if len(path) == 3:
            return human_outcome_menu(path[2])

        return record_human_outcome(path[2], path[3])

    if option == "4":
        if len(path) == 2:
            return ask_farmer_id("Enter Farmer ID to copy farmer SMS:")

        return copy_farmer_sms(path[2])

    if option == "5":
        if len(path) == 2:
            return require_job_id()

        return masumi_job_status(path[2])

    return end("Invalid officer option.")