
from unittest.mock import patch

from intelligence.retrieval_manager import retrieve_financial_news


IDENTITY = {
    "ticker": "RELIANCE.NS",
    "market": "INDIA",
    "company_name": "Reliance Industries Limited",
}

SEARCH_PLAN = {
    "period_days": 7,
    "queries": [
        {
            "category": "company_developments",
            "query": "Reliance company developments",
        },
        {
            "category": "financial_performance",
            "query": "Reliance financial performance",
        },
        {
            "category": "market_reaction",
            "query": "Reliance market reaction",
        },
        {
            "category": "expert_analysis",
            "query": "Reliance analyst opinions",
        },
    ],
}

SOURCES = [
    {"domain": "reuters.com"},
    {"domain": "livemint.com"},
]


def make_article(headline):
    return {
        "headline": f"Reliance Industries {headline}",
        "url": f"https://example.com/{headline.replace(' ', '-')}",
        "source": "Example News",
        "content": "Reliance Industries reported this development.",
        "relevance_score": 0.95,
    }


@patch("intelligence.retrieval_manager.search_tavily")
@patch("intelligence.retrieval_manager.get_sources_by_market")
def test_curated_results_sufficient_no_fallback(
    mock_sources,
    mock_search,
):
    mock_sources.return_value = SOURCES

    mock_search.side_effect = [
        {"articles": [make_article("Reliance investment announcement")]},
        {"articles": [make_article("Reliance revenue growth")]},
        {"articles": [make_article("Reliance share price movement")]},
        {"articles": [make_article("Reliance analyst outlook")]},
    ]

    result = retrieve_financial_news(IDENTITY, SEARCH_PLAN)

    assert len(result["articles"]) == 4
    assert result["curated_article_count"] == 4
    assert result["fallback_categories"] == []

    assert all(
        article["retrieval_tier"] == "curated"
        for article in result["articles"]
    )

    assert mock_search.call_count == 4


@patch("intelligence.retrieval_manager.search_tavily")
@patch("intelligence.retrieval_manager.get_sources_by_market")
def test_fallback_runs_for_category_with_insufficient_coverage(
    mock_sources,
    mock_search,
):
    mock_sources.return_value = SOURCES

    mock_search.side_effect = [
        {"articles": [make_article("Reliance investment announcement")]},
        {"articles": [make_article("Reliance revenue growth")]},
        {"articles": []},
        {"articles": [make_article("Reliance analyst outlook")]},
        {"articles": [make_article("Reliance market reaction analysis")]},
    ]

    result = retrieve_financial_news(IDENTITY, SEARCH_PLAN)

    assert result["curated_article_count"] == 3
    assert result["fallback_categories"] == ["market_reaction"]
    assert mock_search.call_count == 5

    fallback_articles = [
        article
        for article in result["articles"]
        if article["retrieval_tier"] == "fallback"
    ]

    assert len(fallback_articles) == 1
    assert fallback_articles[0]["category"] == "market_reaction"


@patch("intelligence.retrieval_manager.search_tavily")
@patch("intelligence.retrieval_manager.get_sources_by_market")
def test_insufficient_overall_coverage_triggers_all_categories(
    mock_sources,
    mock_search,
):
    mock_sources.return_value = SOURCES

    mock_search.side_effect = [
        {"articles": []},
        {"articles": [make_article("Reliance revenue growth")]},
        {"articles": []},
        {"articles": []},
        {"articles": [make_article("Reliance announces investment development")]},
        {"articles": []},
        {"articles": []},
        {"articles": []},
    ]

    result = retrieve_financial_news(IDENTITY, SEARCH_PLAN)

    assert result["curated_article_count"] == 1

    assert result["fallback_categories"] == [
        "company_developments",
        "financial_performance",
        "market_reaction",
        "expert_analysis",
    ]

    assert mock_search.call_count == 8

    fallback_articles = [
        article
        for article in result["articles"]
        if article["retrieval_tier"] == "fallback"
    ]

    assert len(fallback_articles) == 1


@patch("intelligence.retrieval_manager.search_tavily")
@patch("intelligence.retrieval_manager.get_sources_by_market")
def test_curated_search_error_does_not_crash_retrieval(
    mock_sources,
    mock_search,
):
    mock_sources.return_value = SOURCES

    mock_search.side_effect = [
        {"error": "News search failed", "articles": []},
        {"articles": [make_article("Reliance revenue growth")]},
        {"articles": [make_article("Reliance market reaction")]},
        {"articles": [make_article("Reliance analyst outlook")]},
        {"articles": [make_article("Reliance announces investment development")]},
    ]

    result = retrieve_financial_news(IDENTITY, SEARCH_PLAN)

    assert result["curated_article_count"] == 3
    assert result["fallback_categories"] == ["company_developments"]
    assert len(result["articles"]) == 4

@patch("intelligence.retrieval_manager.search_tavily")
@patch("intelligence.retrieval_manager.get_sources_by_market")
def test_evidence_metadata_is_attached(
    mock_sources,
    mock_search,
):
    mock_sources.return_value = SOURCES

    article = {
        "headline": "Reliance reports quarterly revenue growth",
        "url": "https://www.reuters.com/markets/stocks/example",
        "source": "Reuters",
        "content": (
    "Reliance reported higher revenue and profit "
    "following its investment announcement."
),
        "relevance_score": 0.95,
    }

    mock_search.side_effect = [
        {"articles": [article]},
        {"articles": [make_article("Reliance revenue growth")]},
        {"articles": [make_article("Reliance share price movement")]},
        {"articles": [make_article("Reliance analyst outlook")]},
    ]

    result = retrieve_financial_news(IDENTITY, SEARCH_PLAN)

    print("RETRIEVED ARTICLES:", result["articles"])
    print("REJECTED ARTICLES:", result["rejected_articles"])

    first_article = next(
    item
    for item in result["articles"]
    if item["headline"] == "Reliance reports quarterly revenue growth"
)

    assert first_article["evidence_type"] == "reported_fact"
    assert first_article["publisher_name"] == "Reuters"
    assert first_article["source_verified"] is True
    assert first_article["is_primary_source"] is False

@patch("intelligence.retrieval_manager.search_tavily")
@patch("intelligence.retrieval_manager.get_sources_by_market")
def test_primary_source_metadata_is_attached(
    mock_sources,
    mock_search,
):
    mock_sources.return_value = SOURCES

    article = {
        "headline": "Reliance quarterly financial results",
        "url": "https://www.nseindia.com/companies-listing/corporate-filings",
        "source": "NSE India",
        "content": (
    "The company reported quarterly revenue and profit "
    "following its investment announcement."
),        "relevance_score": 0.95,
    }

    mock_search.side_effect = [
        {"articles": [article]},
        {"articles": [make_article("Reliance revenue growth")]},
        {"articles": [make_article("Reliance share price movement")]},
        {"articles": [make_article("Reliance analyst outlook")]},
    ]

    result = retrieve_financial_news(IDENTITY, SEARCH_PLAN)

    primary_article = next(
        article
        for article in result["articles"]
        if article["headline"] == "Reliance quarterly financial results"
    )

    assert primary_article["evidence_type"] == "primary_source_statement"
    assert primary_article["source_verified"] is True
    assert primary_article["is_primary_source"] is True