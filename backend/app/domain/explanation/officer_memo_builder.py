def build_officer_memo(farmer: dict, scoring_result: dict, fairness: dict) -> str:
    score = scoring_result.get("score")
    probability = scoring_result.get("repayment_readiness_probability")
    tier = scoring_result.get("tier")
    loan_range = scoring_result.get("recommended_loan_range")
    provider = scoring_result.get("provider")

    positive_signals = scoring_result.get("positive_signals", [])
    risk_signals = scoring_result.get("risk_signals", [])
    missing_data = scoring_result.get("missing_data", [])
    alternative_data_used = scoring_result.get("alternative_data_used", [])

    positive_text = "; ".join(positive_signals[:5]) if positive_signals else "No strong positive signals available."
    risk_text = "; ".join(risk_signals[:5]) if risk_signals else "No major risk signals detected."
    missing_text = "; ".join(missing_data[:5]) if missing_data else "No major missing data."
    alternative_text = "; ".join(alternative_data_used[:6]) if alternative_data_used else "No alternative data available."

    return (
        f"Loan Officer Memo\n\n"
        f"Farmer: {farmer['name']} ({farmer['farmer_id']})\n"
        f"Location: {farmer['area']}, {farmer['county']}\n"
        f"Crop/season: {farmer['crop']} during {farmer['season']}\n"
        f"Loan request: KES {farmer['loan_request']:,} for {farmer['loan_purpose']}\n\n"
        f"Scoring provider: {provider}\n"
        f"Repayment-readiness score: {score}/100\n"
        f"Repayment-readiness probability: {probability}\n"
        f"Tier: {tier}\n"
        f"Suggested support range: {loan_range}\n\n"
        f"Alternative evidence used: {alternative_text}\n\n"
        f"Positive signals: {positive_text}\n\n"
        f"Risk signals: {risk_text}\n\n"
        f"Missing data: {missing_text}\n\n"
        f"Responsible AI note: {fairness.get('note')}\n\n"
        f"Boundary: This agent prepares decision support only. "
        f"The human loan officer must make and record the final review outcome."
    )