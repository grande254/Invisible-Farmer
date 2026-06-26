from app.domain.farmer.repository import get_farmer_by_id
from app.domain.review.review_orchestrator import create_credit_review
from app.domain.ussd.ussd_screen_builder import compact, con, end, parse_ussd_path


def farmer_main_menu() -> dict:
    return con(
        "Invisible Farmer\n"
        "1. Check review status\n"
        "2. Request credit review\n"
        "3. Improvement tips\n"
        "4. Contact loan officer\n"
        "0. Exit"
    )


def ask_farmer_id(action: str) -> dict:
    labels = {
        "status": "Enter your Farmer ID to check review status:",
        "request": "Enter your Farmer ID to request credit review:",
        "tips": "Enter your Farmer ID to view improvement tips:",
        "contact": "Enter your Farmer ID to contact loan officer:",
    }

    return con(labels.get(action, "Enter your Farmer ID:"))


def farmer_status(farmer_id: str) -> dict:
    farmer = get_farmer_by_id(farmer_id)

    if not farmer:
        return end(
            "Farmer ID not found. Please confirm your ID with the branch loan officer."
        )

    review = create_credit_review(farmer_id)
    decision_support = review["decision_support"]

    credit = decision_support["credit_readiness"]
    farmer_message = decision_support["farmer_message"]

    ussd_summary = farmer_message.get("ai_ussd_summary")

    if not ussd_summary:
        ussd_summary = (
            f"Review complete\n"
            f"Tier: {credit.get('tier')}\n"
            f"Score: {credit.get('score')}/100\n"
            f"Possible support: {credit.get('recommended_loan_range')}\n"
            f"Loan officer final decision required."
        )

    return end(compact(ussd_summary, 180))


def farmer_request_review(farmer_id: str) -> dict:
    farmer = get_farmer_by_id(farmer_id)

    if not farmer:
        return end(
            "Farmer ID not found. Visit or call your branch loan officer for registration."
        )

    review = create_credit_review(farmer_id)
    credit = review["decision_support"]["credit_readiness"]

    return end(
        compact(
            f"Review request received. Tier: {credit.get('tier')}. "
            f"Score: {credit.get('score')}/100. "
            f"Loan officer final decision required.",
            180,
        )
    )


def farmer_improvement_tips(farmer_id: str) -> dict:
    farmer = get_farmer_by_id(farmer_id)

    if not farmer:
        return end(
            "Farmer ID not found. Please confirm your ID with the branch loan officer."
        )

    review = create_credit_review(farmer_id)
    tips = review["decision_support"]["farmer_message"].get("improvement_tips", [])

    if not tips:
        return end("Keep repayment, sales, savings group, and input purchase records.")

    text = "Tips:\n" + "\n".join([f"- {tip}" for tip in tips[:3]])

    return end(compact(text, 180))


def farmer_contact_officer(farmer_id: str) -> dict:
    farmer = get_farmer_by_id(farmer_id)

    if not farmer:
        return end(
            "Farmer ID not found. Please visit the nearest branch for support."
        )

    return end(
        "Visit your branch loan officer with your ID, farming records, sales records, "
        "savings group records, or cooperative records."
    )


def handle_farmer_ussd(text: str | None, phone_number: str | None = None) -> dict:
    path = parse_ussd_path(text)

    if not path:
        return farmer_main_menu()

    first = path[0]

    if first == "0":
        return end("Thank you for using Invisible Farmer.")

    if first == "1":
        if len(path) == 1:
            return ask_farmer_id("status")

        return farmer_status(path[1])

    if first == "2":
        if len(path) == 1:
            return ask_farmer_id("request")

        return farmer_request_review(path[1])

    if first == "3":
        if len(path) == 1:
            return ask_farmer_id("tips")

        return farmer_improvement_tips(path[1])

    if first == "4":
        if len(path) == 1:
            return ask_farmer_id("contact")

        return farmer_contact_officer(path[1])

    return end("Invalid option. Please try again.")