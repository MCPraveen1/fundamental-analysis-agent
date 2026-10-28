from agents.report_evaluator import evaluate_report_claims


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


def test_allows_persistent_trend_with_three_periods():
    issues = evaluate_report_claims(
        "Revenue shows a persistent trend.",
        reporting_period_count=3,
    )

    assert (
        "Insufficient periods to support persistent trend"
        not in issues
    )


def test_allows_leverage_claim_with_debt_data():
    issues = evaluate_report_claims(
        "The company is highly leveraged.",
        has_debt_data=True,
    )

    assert "Leverage claim lacks debt data" not in issues

