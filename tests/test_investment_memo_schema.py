
import pytest
from pydantic import ValidationError

from agents.investment_memo_schema import InvestmentMemo


def test_valid_investment_memo():
    memo = InvestmentMemo(
        ticker="AAPL",
        company_name="Apple Inc.",
        currency="USD",
        financial_analysis={
            "summary": "Financial analysis completed."
        },
        price_analysis={
            "current_price": 225.50,
            "currency": "USD",
        },
        key_strengths=["Positive cash flow"],
        overall_summary="Illustrative investment memo.",
    )

    assert memo.ticker == "AAPL"
    assert memo.price_analysis["current_price"] == 225.50
    assert memo.recommendation == "NOT_ASSESSED"
    assert memo.key_concerns == []
    assert memo.risks_and_limitations == []


def test_missing_required_field_is_rejected():
    with pytest.raises(ValidationError):
        InvestmentMemo(
            ticker="AAPL",
            financial_analysis={},
            price_analysis={},
        )


def test_custom_recommendation_can_be_supplied():
    memo = InvestmentMemo(
        ticker="AAPL",
        financial_analysis={},
        price_analysis={},
        overall_summary="Illustrative memo.",
        recommendation="NOT_ASSESSED",
    )

    assert memo.recommendation == "NOT_ASSESSED"


def test_news_analysis_defaults_to_empty_dictionary():
    memo = InvestmentMemo(
        ticker="AAPL",
        financial_analysis={},
        price_analysis={},
        overall_summary="Illustrative investment memo.",
    )

    assert memo.news_analysis == {}

import pytest
from pydantic import ValidationError

from agents.investment_memo_schema import (
    InvestmentMemo,
    Recommendation,
)


def test_default_recommendation():
    memo = InvestmentMemo(
        ticker="AAPL",
        financial_analysis={},
        price_analysis={},
        overall_summary="Test summary",
    )

    assert memo.recommendation == Recommendation.NOT_ASSESSED


@pytest.mark.parametrize(
    "recommendation",
    ["BUY", "HOLD", "SELL", "NOT_ASSESSED"],
)
def test_valid_recommendations(recommendation):
    memo = InvestmentMemo(
        ticker="AAPL",
        financial_analysis={},
        price_analysis={},
        overall_summary="Test summary",
        recommendation=recommendation,
    )

    assert memo.recommendation == recommendation


def test_invalid_recommendation():
    with pytest.raises(ValidationError):
        InvestmentMemo(
            ticker="AAPL",
            financial_analysis={},
            price_analysis={},
            overall_summary="Test summary",
            recommendation="MAYBE",
        )

    