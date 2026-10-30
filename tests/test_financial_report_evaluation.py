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

def test_accepts_revenue_growth_supported_by_historical_data():
    narrative = (
        "Revenue grew from $383.3B in 2023 "
        "to $416.2B in 2025."
    )

    evidence = {
        "history": {
            "revenue": [
                {"period": "2023", "value": 383.3},
                {"period": "2025", "value": 416.2},
            ]
        }
    }

    issues = evaluate_report_claims(
        narrative,
        evidence=evidence,
    )

    assert "Unsupported revenue growth claim" not in issues

def test_flags_revenue_growth_claim_not_supported_by_data():
    narrative = (
        "Revenue grew from $383.3B in 2023 "
        "to $450B in 2025."
    )

    evidence = {
        "history": {
            "revenue": [
                {"period": "2023", "value": 383.3},
                {"period": "2025", "value": 416.2},
            ]
        }
    }

    issues = evaluate_report_claims(
        narrative,
        evidence=evidence,
    )

    assert "Unsupported revenue growth claim" in issues

def test_flags_incorrect_revenue_growth_direction():
    narrative = (
        "Revenue declined from $383.3B in 2023 "
        "to $416.2B in 2025."
    )

    evidence = {
        "history": {
            "revenue": [
                {"period": "2023", "value": 383.3},
                {"period": "2025", "value": 416.2},
            ]
        }
    }

    issues = evaluate_report_claims(
        narrative,
        evidence=evidence,
    )

    assert "Unsupported revenue growth claim" in issues


def test_flags_incorrect_revenue_claim_expressed_in_billions():
    narrative = (
        "Revenue grew from $383.3 billion in 2023 "
        "to $450 billion in 2025."
    )

    evidence = {
        "history": {
            "revenue": [
                {"period": "2023", "value": 383.285},
                {"period": "2025", "value": 416.161},
            ]
        }
    }

    issues = evaluate_report_claims(
        narrative,
        evidence=evidence,
    )

    assert "Unsupported revenue growth claim" in issues

def test_accepts_revenue_growth_expressed_in_billions():
    narrative = (
        "Revenue grew from $383.3 billion in 2023 "
        "to $416.2 billion in 2025, showing an upward trend."
    )

    evidence = {
        "history": {
            "revenue": [
                {"period": "2023", "value": 383.285},
                {"period": "2025", "value": 416.161},
            ]
        }
    }

    issues = evaluate_report_claims(
        narrative,
        evidence=evidence,
    )

    assert "Unsupported revenue growth claim" not in issues
