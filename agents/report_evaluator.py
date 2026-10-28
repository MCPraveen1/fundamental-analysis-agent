
def evaluate_report_claims(
    narrative,
    has_industry_benchmarks=False,
    reporting_period_count=0,
    has_debt_data=False,
):
    """Flag selected financial claims that need supporting evidence."""

    text = narrative.lower()
    issues = []

    industry_phrases = (
        "above industry averages",
        "below industry averages",
        "outperforms the industry",
        "underperforms the industry",
    )

    if not has_industry_benchmarks and any(
        phrase in text for phrase in industry_phrases
    ):
        issues.append("Unsupported industry comparison")

    persistent_trend_phrases = (
        "persistent trend",
        "long-term trend",
        "consistently increasing",
        "consistently declining",
    )

    if reporting_period_count < 3 and any(
        phrase in text for phrase in persistent_trend_phrases
    ):
        issues.append(
            "Insufficient periods to support persistent trend"
        )

    leverage_phrases = (
        "highly leveraged",
        "excessive leverage",
        "high debt burden",
    )

    if not has_debt_data and any(
        phrase in text for phrase in leverage_phrases
    ):
        issues.append("Leverage claim lacks debt data")

    return issues
