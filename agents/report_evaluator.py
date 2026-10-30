
def evaluate_report_claims(
    narrative,
    has_industry_benchmarks=False,
    reporting_period_count=0,
    has_debt_data=False,
    evidence=None,
):
    """Flag financial claims that need supporting evidence."""

    text = narrative.lower()
    issues = []
    evidence = evidence or {}

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

        revenue_history = (
        evidence.get("history", {}).get("revenue", [])
    )

    import re

    if (
        "revenue grew from" in text
        or "revenue declined from" in text
    ):
        matches = re.search(
            r"revenue (grew|declined) from \$([\d,.]+)\s*(billion|b) in (\d{4}) "
            r"to \$([\d,.]+)\s*(billion|b) in (\d{4})",
            text,
        )

        if matches and isinstance(revenue_history, list):
            claimed_direction = matches.group(1)

            start_value = float(
                matches.group(2).replace(",", "")
            )
            start_period = matches.group(4)

            end_value = float(
                matches.group(5).replace(",", "")
            )
            end_period = matches.group(7)

            actual_direction = (
                "grew" if end_value > start_value
                else "declined" if end_value < start_value
                else "unchanged"
            )

            if claimed_direction != actual_direction:
                issues.append(
                    "Unsupported revenue growth claim"
                )
            else:
                history_by_period = {
                    str(record.get("period"))[:4]: float(
                        record.get("value")
                    )
                    for record in revenue_history
                    if isinstance(record, dict)
                    and record.get("value") is not None
                }

                source_start = history_by_period.get(start_period)
                source_end = history_by_period.get(end_period)

                # Allow for figures rounded to one decimal place.
                tolerance = 0.05

                if (
                    source_start is None
                    or source_end is None
                    or abs(source_start - start_value) > tolerance
                    or abs(source_end - end_value) > tolerance
                ):
                    issues.append(
                        "Unsupported revenue growth claim"
                    )

    return issues
