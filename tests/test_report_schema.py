
import pytest
from pydantic import ValidationError

from agents.report_schema import (
    FinancialAnalysisReport,
    FinancialMetrics,
)


def test_valid_report():
    report = FinancialAnalysisReport(
        ticker="AAPL",
        company_name="Apple Inc.",
        currency="USD",
        data_source="Test provider",
        metrics=FinancialMetrics(
            profit_margin=0.10,
            free_cash_flow=140,
        ),
        strengths=["Positive free cash flow"],
        summary="Illustrative test report.",
    )

    assert report.ticker == "AAPL"
    assert report.metrics.free_cash_flow == 140
    assert report.concerns == []
    assert report.metrics.operating_margin is None


def test_missing_required_field_is_rejected():
    with pytest.raises(ValidationError):
        FinancialAnalysisReport(
            ticker="AAPL",
            data_source="Test provider",
            metrics={},
        )
