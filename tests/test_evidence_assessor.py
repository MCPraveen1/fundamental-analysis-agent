
import pytest

from intelligence.evidence_assessor import (
    assess_evidence,
    normalize_text,
)


def test_primary_source_statement():
    article = {
        "headline": "Reliance publishes official announcement",
        "content": "The company issued an official announcement.",
        "source": "National Stock Exchange of India",
        "url": "https://www.nseindia.com/companies-listing/corporate-filings",
    }

    result = assess_evidence(article)

    assert result["evidence_type"] == "primary_source_statement"
    assert result["is_forecast"] is False
    assert result["requires_verification"] is False
    assert result["source_verified"] is True
    assert result["is_primary_source"] is True

def test_reported_financial_fact():
    article = {
        "headline": "Reliance reports quarterly revenue growth",
        "content": "The company reported higher revenue and profit.",
        "source": "Reuters",
    }

    result = assess_evidence(article)

    assert result["evidence_type"] == "reported_fact"
    assert result["is_forecast"] is False


def test_analyst_opinion():
    article = {
        "headline": "Brokerage upgrades Reliance rating",
        "content": "The analyst issued a positive recommendation.",
        "source": "Financial News",
    }

    result = assess_evidence(article)

    assert result["evidence_type"] == "analyst_opinion"


def test_forecast():
    article = {
        "headline": "Reliance revenue expected to increase",
        "content": "The company is projected to achieve higher revenue.",
        "source": "Financial News",
    }

    result = assess_evidence(article)

    assert result["evidence_type"] == "forecast"
    assert result["is_forecast"] is True


def test_forecast_takes_priority_over_analyst_opinion():
    article = {
        "headline": "Analyst forecasts Reliance revenue growth",
        "content": "The brokerage expects earnings to increase.",
        "source": "Financial News",
    }

    result = assess_evidence(article)

    assert result["evidence_type"] == "forecast"
    assert result["is_forecast"] is True


def test_analyst_opinion_takes_priority_over_reported_fact():
    article = {
        "headline": "Analyst reviews Reliance financial performance",
        "content": "The analyst discusses revenue and profit.",
        "source": "Financial News",
    }

    result = assess_evidence(article)

    assert result["evidence_type"] == "analyst_opinion"


def test_unverified_claim():
    article = {
        "headline": "Reliance business developments",
        "content": "The article contains insufficient financial details.",
        "source": "Unknown Source",
    }

    result = assess_evidence(article)

    assert result["evidence_type"] == "unverified_claim"
    assert result["requires_verification"] is True


def test_empty_article_content():
    article = {
        "headline": "",
        "content": "",
        "source": "Unknown",
    }

    result = assess_evidence(article)

    assert result["evidence_type"] == "unverified_claim"
    assert result["requires_verification"] is True


def test_invalid_article_is_rejected():
    with pytest.raises(ValueError):
        assess_evidence("not an article")


def test_normalize_text():
    assert normalize_text("  Reliance   REVENUE  ") == (
        "reliance revenue"
    )

def test_news_publisher_reporting_official_announcement():
    article = {
        "headline": "Reliance publishes official announcement",
        "content": "The company announced a new investment.",
        "url": "https://www.reuters.com/markets/stocks/example",
    }

    result = assess_evidence(article)

    assert result["evidence_type"] == "reported_fact"
    assert result["source_verified"] is True
    assert result["is_primary_source"] is False

def test_unknown_publisher_is_not_primary_source():
    article = {
        "headline": "Reliance publishes official announcement",
        "content": "The company issued an official announcement.",
        "url": "https://example.com/reliance-news",
    }

    result = assess_evidence(article)

    assert result["evidence_type"] == "unverified_claim"
    assert result["source_verified"] is False
    assert result["is_primary_source"] is False