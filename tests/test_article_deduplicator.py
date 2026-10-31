
import pytest

from intelligence.article_deduplicator import (
    deduplicate_articles,
    normalize_headline,
    normalize_url,
)


def make_article(
    headline,
    url,
    retrieval_tier="curated",
    category="company_developments",
):
    return {
        "headline": headline,
        "url": url,
        "source": "Example News",
        "content": "Example financial news content.",
        "retrieval_tier": retrieval_tier,
        "category": category,
        "matched_categories": [category],
    }


def test_duplicate_urls_are_merged():
    articles = [
        make_article(
            "Reliance announces investment",
            "https://example.com/news/1",
        ),
        make_article(
            "Different headline",
            "https://example.com/news/1",
            retrieval_tier="fallback",
        ),
    ]

    result = deduplicate_articles(articles)

    assert len(result) == 1
    assert result[0]["retrieval_tiers"] == ["curated", "fallback"]


def test_tracking_parameters_do_not_create_duplicates():
    url1 = "https://www.example.com/news/1?utm_source=google"
    url2 = "https://example.com/news/1?utm_medium=email"

    assert normalize_url(url1) == normalize_url(url2)

    articles = [
        make_article("Reliance investment", url1),
        make_article("Another headline", url2, retrieval_tier="fallback"),
    ]

    result = deduplicate_articles(articles)

    assert len(result) == 1


def test_duplicate_headlines_are_merged():
    articles = [
        make_article(
            "Reliance announces major investment!",
            "https://example.com/news/1",
        ),
        make_article(
            "Reliance announces major investment",
            "https://another-example.com/news/2",
            retrieval_tier="fallback",
        ),
    ]

    result = deduplicate_articles(articles)

    assert len(result) == 1
    assert result[0]["retrieval_tiers"] == ["curated", "fallback"]


def test_different_articles_are_retained():
    articles = [
        make_article(
            "Reliance announces investment",
            "https://example.com/news/1",
        ),
        make_article(
            "Reliance reports quarterly earnings",
            "https://example.com/news/2",
        ),
    ]

    result = deduplicate_articles(articles)

    assert len(result) == 2


def test_retrieval_categories_are_preserved():
    articles = [
        make_article(
            "Reliance financial results",
            "https://example.com/news/1",
            category="financial_performance",
        ),
        make_article(
            "Different headline",
            "https://example.com/news/1",
            retrieval_tier="fallback",
            category="expert_analysis",
        ),
    ]

    result = deduplicate_articles(articles)

    assert len(result) == 1
    assert result[0]["retrieval_categories"] == [
        "expert_analysis",
        "financial_performance",
    ]
    assert result[0]["matched_categories"] == [
        "expert_analysis",
        "financial_performance",
    ]


def test_invalid_article_entries_are_skipped():
    articles = [
        None,
        "invalid article",
        {},
        make_article(
            "Reliance announces investment",
            "https://example.com/news/1",
        ),
    ]

    result = deduplicate_articles(articles)

    assert len(result) == 1


def test_non_list_input_is_rejected():
    with pytest.raises(ValueError):
        deduplicate_articles("not a list")


def test_headline_normalization():
    assert normalize_headline(
        "  Reliance Announces Investment!  "
    ) == "reliance announces investment"
