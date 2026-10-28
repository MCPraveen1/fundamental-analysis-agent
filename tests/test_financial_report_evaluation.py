from agents.report_evaluator import evaluate_report_claims


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
        issues.append("Insufficient periods to support persistent trend")

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


def test_flags_unsupported_industry_comparison():
    issues = evaluate_report_claims(
        "Profit margins are above industry averages."
    )

    assert "Unsupported industry comparison" in issues


def test_allows_industry_comparison_with_benchmarks():
    issues = evaluate_report_claims(
        "Profit margins are above industry averages.",
        has_industry_benchmarks=True,
    )

    assert "Unsupported industry comparison" not in issues


def test_flags_persistent_trend_with_too_few_periods():
    issues = evaluate_report_claims(
        "Revenue shows a persistent trend.",
        reporting_period_count=2,
    )

    assert "Insufficient periods to support persistent trend" in issues


def test_flags_leverage_claim_without_debt_data():
    issues = evaluate_report_claims(
        "The company is highly leveraged.",
        has_debt_data=False,
    )

    assert "Leverage claim lacks debt data" in issues
