def build_farmer_sms(farmer: dict, scoring_result: dict) -> str:
    tier = scoring_result.get("tier", "Not Available")
    loan_range = scoring_result.get("recommended_loan_range", "Not available")
    score = scoring_result.get("score", "N/A")

    if tier == "Not Ready":
        return (
            f"Invisible Farmer: Your credit-readiness review is complete. "
            f"Tier: {tier}. Score: {score}/100. "
            f"Recommended next step: build more records before loan processing. "
            f"Loan officer final decision required."
        )

    return (
        f"Invisible Farmer: Your credit-readiness review is complete. "
        f"Tier: {tier}. Score: {score}/100. Possible support range: {loan_range}. "
        f"Loan officer final decision required."
    )


def build_farmer_improvement_tips(farmer: dict, scoring_result: dict) -> list[str]:
    tips = []

    missing_data = scoring_result.get("missing_data", [])
    risk_signals = scoring_result.get("risk_signals", [])

    if "mobile money consistency" in missing_data:
        tips.append("Keep regular mobile money transaction records linked to farming activity.")

    if "cooperative repayment score" in missing_data:
        tips.append("Ask your cooperative or group to record repayment and contribution history.")

    if "market payment consistency" in missing_data:
        tips.append("Keep buyer payment records after selling produce.")

    if "input purchase frequency" in missing_data:
        tips.append("Keep receipts for seed, fertilizer, pesticide, and other input purchases.")

    if "sales records" in missing_data:
        tips.append("Record produce sales, buyer name, date, quantity, and amount.")

    if "formal credit history" in missing_data:
        tips.append("Use small formal products where available to build a track record.")

    if any("drought" in signal.lower() for signal in risk_signals):
        tips.append("Discuss drought timing, irrigation plans, or climate risk mitigation with the loan officer.")

    if any("pest" in signal.lower() for signal in risk_signals):
        tips.append("Keep extension officer or input supplier records for pest-control support.")

    if not tips:
        tips.append("Continue keeping repayment, sales, input purchase, and group contribution records.")

    return tips[:5]


def build_farmer_ussd_summary(farmer: dict, scoring_result: dict) -> dict:
    language = farmer.get("preferred_language", "en")
    tier = scoring_result.get("tier", "N/A")
    score = scoring_result.get("score", "N/A")
    loan_range = scoring_result.get("recommended_loan_range", "Not available")

    if language == "sw":
        screen_1 = (
            "Invisible Farmer\n"
            "1. Angalia hali ya ukaguzi\n"
            "2. Omba ukaguzi wa mkopo\n"
            "3. Vidokezo vya kuboresha\n"
            "0. Toka"
        )

        screen_2 = (
            f"Hali ya Ukaguzi\n"
            f"Kiwango: {tier}\n"
            f"Alama: {score}/100\n"
            f"Kiwango kinachowezekana: {loan_range}\n"
            f"Afisa wa mkopo lazima afanye uamuzi wa mwisho."
        )
    else:
        screen_1 = (
            "Invisible Farmer\n"
            "1. Check review status\n"
            "2. Request credit review\n"
            "3. View improvement tips\n"
            "0. End"
        )

        screen_2 = (
            f"Review Status\n"
            f"Tier: {tier}\n"
            f"Score: {score}/100\n"
            f"Possible support: {loan_range}\n"
            f"Loan officer final decision required."
        )

    return {
        "farmer_id": farmer["farmer_id"],
        "language": language,
        "ussd_code": "*384*55#",
        "screens": [
            {
                "screen": 1,
                "type": "CON",
                "text": screen_1,
            },
            {
                "screen": 2,
                "type": "END",
                "text": screen_2,
            },
        ],
    }