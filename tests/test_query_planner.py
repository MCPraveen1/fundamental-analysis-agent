import pytest

from intelligence.query_planner import build_search_queries


RELIANCE_IDENTITY = {
    "ticker": "RELIANCE.NS",
    "company_name": "Reliance Industries Limited",
    "market": "INDIA",
    "exchange": "NSE",
    "currency": "INR",
}


APPLE_IDENTITY = {
    "ticker": "AAPL",
    "company_name": "Apple Inc.",
    "market": "US",
    "exchange": "US_MARKET",
    "currency": "USD",
}


def test_default_period_is_seven_days():
    result = build_search_queries(RELIANCE_IDENTITY)

    assert result["period_days"] == 7


def test_four_query_categories_are_generated():
    result = build_search_queries(RELIANCE_IDENTITY)

    categories = [item["category"] for item in result["queries"]]

    assert categories == [
        "company_developments",
        "financial_performance",
        "market_reaction",
        "expert_analysis",
    ]


def test_indian_company_queries_use_company_name():
    result = build_search_queries(RELIANCE_IDENTITY)

    assert all(
        "Reliance Industries Limited" in item["query"]
        for item in result["queries"]
    )


def test_indian_market_reaction_query_uses_exchange():
    result = build_search_queries(RELIANCE_IDENTITY)

    market_query = next(
        item["query"]
        for item in result["queries"]
        if item["category"] == "market_reaction"
    )

    assert "NSE India" in market_query


def test_us_market_reaction_query_uses_us_market():
    result = build_search_queries(APPLE_IDENTITY)

    market_query = next(
        item["query"]
        for item in result["queries"]
        if item["category"] == "market_reaction"
    )

    assert "US stock market" in market_query


def test_custom_period_is_preserved():
    result = build_search_queries(RELIANCE_IDENTITY, period_days=30)

    assert result["period_days"] == 30


def test_incomplete_identity_is_rejected():
    with pytest.raises(ValueError, match="Company identity is incomplete"):
        build_search_queries({"ticker": "AAPL"})


def test_invalid_period_is_rejected():
    with pytest.raises(ValueError, match="period_days must be at least 1"):
        build_search_queries(RELIANCE_IDENTITY, period_days=0)


def test_non_integer_period_is_rejected():
    with pytest.raises(ValueError, match="period_days must be an integer"):
        build_search_queries(RELIANCE_IDENTITY, period_days="7")


def test_unsupported_market_is_rejected():
    identity = {
        **RELIANCE_IDENTITY,
        "market": "EUROPE",
    }

    with pytest.raises(ValueError, match="Unsupported market"):
        build_search_queries(identity)