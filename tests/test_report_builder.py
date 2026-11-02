import pytest

from intelligence.report_builder import (
    build_financial_intelligence_report,
)


def test_build_report_groups_articles_by_category():
    news_analysis = {
        "ticker": "RELIANCE.NS",
        "articles": [
            {
                "headline": "Reliance reports quarterly results",
                "category": "financial_performance",
                "matched_categories": [
                    "financial_performance",
                    "company_developments",
                ],
                "evidence_type": "reported_fact",
                "source_type": "financial_news",
                "source_verified": True,
            },
            {
                "headline": "Reliance announces new investment",
                "category": "company_developments",
                "matched_categories": ["company_developments"],
                "evidence_type": "primary_source_statement",
                "source_type": "primary_source",
                "source_verified": True,
            },
        ],
    }

    report = build_financial_intelligence_report(news_analysis)

    assert len(report["news_categories"]["financial_performance"]) == 1
    assert len(report["news_categories"]["company_developments"]) == 2


def test_build_report_counts_evidence_types():
    news_analysis = {
        "ticker": "AAPL",
        "articles": [
            {"evidence_type": "reported_fact"},
            {"evidence_type": "reported_fact"},
            {"evidence_type": "analyst_opinion"},
            {"evidence_type": "forecast"},
            {"evidence_type": "unverified_claim"},
        ],
    }

    report = build_financial_intelligence_report(news_analysis)

    counts = report["evidence_summary"]["evidence_type_counts"]

    assert counts["reported_fact"] == 2
    assert counts["analyst_opinion"] == 1
    assert counts["forecast"] == 1
    assert counts["unverified_claim"] == 1
    assert counts["primary_source_statement"] == 0


def test_build_report_classifies_source_quality():
    news_analysis = {
        "ticker": "AAPL",
        "articles": [
            {
                "source_type": "primary_source",
                "is_primary_source": True,
                "source_verified": True,
            },
            {
                "source_type": "financial_news",
                "is_primary_source": False,
                "source_verified": True,
            },
            {
                # An unregistered publisher must remain unknown.
                "is_primary_source": False,
                "source_verified": False,
            },
        ],
    }

    report = build_financial_intelligence_report(news_analysis)

    source_quality = report["source_quality"]

    assert source_quality["primary_source_count"] == 1
    assert source_quality["secondary_source_count"] == 1
    assert source_quality["unknown_source_count"] == 1
    assert source_quality["verified_publisher_count"] == 2


def test_build_report_preserves_retrieval_limitations():
    news_analysis = {
        "ticker": "RELIANCE.NS",
        "articles": [
            {
                "evidence_status": "metadata_incomplete",
                "requires_verification": True,
                "source_type": "financial_news",
            }
        ],
        "rejected_articles": [{"headline": "Unrelated article"}],
        "search_errors": [{"category": "market_reaction", "error": "Timeout"}],
        "category_counts": {"company_developments": 1},
        "fallback_categories": ["market_reaction"],
        "curated_article_count": 1,
        "total_unique_articles": 1,
    }

    report = build_financial_intelligence_report(news_analysis)

    assert report["retrieval_summary"]["rejected_article_count"] == 1
    assert report["retrieval_summary"]["search_error_count"] == 1
    assert report["retrieval_summary"]["fallback_categories"] == [
        "market_reaction"
    ]

    assert report["evidence_summary"]["verification_required_count"] == 1

    assert any(
        "search operation" in limitation
        for limitation in report["limitations"]
    )
    assert any(
        "incomplete" in limitation
        for limitation in report["limitations"]
    )
    assert any(
        "require" in limitation
        for limitation in report["limitations"]
    )


def test_build_report_handles_empty_articles():
    news_analysis = {
        "ticker": "AAPL",
        "articles": [],
    }

    report = build_financial_intelligence_report(news_analysis)

    assert report["retrieval_summary"]["total_unique_articles"] == 0
    assert report["limitations"] == [
        "No relevant articles were retrieved."
    ]


def test_build_report_rejects_invalid_input():
    with pytest.raises(ValueError, match="dictionary"):
        build_financial_intelligence_report([])


def test_build_report_rejects_failed_news_analysis():
    news_analysis = {
        "ticker": "AAPL",
        "error": "News retrieval failed",
    }

    with pytest.raises(ValueError, match="failed news analysis"):
        build_financial_intelligence_report(news_analysis)


def test_build_report_requires_ticker():
    news_analysis = {
        "articles": [],
    }

    with pytest.raises(ValueError, match="ticker"):
        build_financial_intelligence_report(news_analysis)

def test_build_report_rejects_non_list_articles():
    news_analysis = {
        "ticker": "AAPL",
        "articles": {},
    }

    with pytest.raises(ValueError, match="list"):
        build_financial_intelligence_report(news_analysis)