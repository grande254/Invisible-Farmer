def tier_from_score(score: int) -> tuple[str, str]:
    if score >= 80:
        return "Gold", "KES 20,000–30,000"

    if score >= 60:
        return "Silver", "KES 10,000–20,000"

    if score >= 40:
        return "Bronze", "KES 5,000–10,000"

    return "Not Ready", "Record-building support recommended first"