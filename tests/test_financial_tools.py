
import pytest

from tools.financial_tools import calculate_ratios


def test_calculates_financial_ratios():
    financials = {
        "revenue": 1000,
        "net_income": 100,
        "operating_income": 150,
        "total_assets": 500,
        "shareholders_equity": 250,
        "operating_cash_flow": 180,
        "capital_expenditure": -40,
    }

    ratios = calculate_ratios(financials)

    assert ratios["profit_margin"] == pytest.approx(0.10)
    assert ratios["operating_margin"] == pytest.approx(0.15)
    assert ratios["return_on_assets"] == pytest.approx(0.20)
    assert ratios["return_on_equity"] == pytest.approx(0.40)
    assert ratios["free_cash_flow"] == pytest.approx(140)


def test_handles_zero_revenue():
    financials = {
        "revenue": 0,
        "net_income": 100,
        "operating_income": 150,
        "total_assets": 500,
        "shareholders_equity": 250,
        "operating_cash_flow": 180,
        "capital_expenditure": -40,
    }

    ratios = calculate_ratios(financials)

    assert ratios["profit_margin"] is None
    assert ratios["operating_margin"] is None


def test_handles_missing_financial_data():
    ratios = calculate_ratios({})

    assert ratios["profit_margin"] is None
    assert ratios["operating_margin"] is None
    assert ratios["return_on_assets"] is None
    assert ratios["return_on_equity"] is None
    assert ratios["free_cash_flow"] is None
