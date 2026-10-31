
import pytest

from intelligence.relevance_classifier import (
    classify_article_relevance,
    normalize_text,
    contains_company_reference,
)


IDENTITY = {
    "ticker": "RELIANCE.NS",
    "company_name": "Reliance Industries Limited",
}


def test_direct_company_reference_in_headline():
    article = {
        "headline": "Reliance Industries announces major investment",
        "content": "The company announced a new investment project.",
    }

    result = classify_article_relevance(article, IDENTITY)

    assert result["company_relevance"] == "direct"
    assert "company_developments" in result["matched_categories"]
    assert result["is_relevant"] is True


def test_company_mentioned_only_in_content():
    article = {
        "headline": "Indian stock market closes higher",
        "content": "Reliance Industries shares gained during trading.",
    }

    result = classify_article_relevance(article, IDENTITY)

    assert result["company_relevance"] == "mention"
    assert result["is_relevant"] is False


def test_unrelated_company_article():
    article = {
        "headline": "TCS reports quarterly earnings growth",
        "content": "The company reported strong revenue.",
    }

    result = classify_article_relevance(article, IDENTITY)

    assert result["company_relevance"] == "unrelated"
    assert result["is_relevant"] is False


def test_ticker_reference_in_headline():
    article = {
        "headline": "RELIANCE.NS shares surge after earnings announcement",
        "content": "The company reported strong results.",
    }

    result = classify_article_relevance(article, IDENTITY)

    assert result["company_relevance"] == "direct"
    assert result["is_relevant"] is True


def test_multiple_financial_categories_are_detected():
    article = {
        "headline": "Reliance shares surge after strong quarterly results",
        "content": "Revenue and profit increased significantly.",
    }

    result = classify_article_relevance(article, IDENTITY)

    assert "financial_performance" in result["matched_categories"]
    assert "market_reaction" in result["matched_categories"]
    assert result["is_relevant"] is True


def test_article_without_category_keywords_is_not_relevant():
    article = {
        "headline": "Reliance Industries appoints a new executive",
        "content": "The company announced the appointment.",
    }

    result = classify_article_relevance(article, IDENTITY)

    assert result["company_relevance"] == "direct"
    assert result["matched_categories"] == []
    assert result["is_relevant"] is False


def test_company_reference_matching_is_case_insensitive():
    assert contains_company_reference(
        "RELIANCE INDUSTRIES announces investment",
        "Reliance Industries Limited",
        "RELIANCE.NS",
    )


def test_normalize_text():
    assert normalize_text("  Reliance   INDUSTRIES  ") == (
        "reliance industries"
    )


def test_invalid_article_is_rejected():
    with pytest.raises(ValueError):
        classify_article_relevance("not an article", IDENTITY)


def test_incomplete_identity_is_rejected():
    with pytest.raises(ValueError):
        classify_article_relevance(
            {"headline": "Reliance announces investment"},
            {"ticker": "RELIANCE.NS"},
        )
