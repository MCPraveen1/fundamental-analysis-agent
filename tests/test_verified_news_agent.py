
from agents.verified_news_agent import VerifiedNewsAgent


def test_complete_article_has_metadata_complete_status():
    def fake_search(ticker, max_results=5):
        return {
            "provider": "Test provider",
            "articles": [
                {
                    "headline": "Company reports quarterly results",
                    "url": "https://example.com/news",
                    "source": "Example News",
                    "published_at": "2026-10-27",
                    "content": "The company reported its results.",
                    "relevance_score": 0.95,
                }
            ],
        }

    agent = VerifiedNewsAgent(news_search=fake_search)
    result = agent.analyse("aapl")

    article = result["articles"][0]

    assert result["ticker"] == "AAPL"
    assert article["evidence_status"] == "metadata_complete"
    assert article["evidence_issues"] == []
    assert article["claims_independently_verified"] is False


def test_missing_metadata_marks_article_incomplete():
    def fake_search(ticker, max_results=5):
        return {
            "provider": "Test provider",
            "articles": [
                {
                    "headline": "Company news",
                    "url": "https://example.com/news",
                    "source": None,
                    "published_at": None,
                    "content": None,
                }
            ],
        }

    agent = VerifiedNewsAgent(news_search=fake_search)
    result = agent.analyse("AAPL")

    article = result["articles"][0]

    assert article["evidence_status"] == "incomplete"
    assert "Source is unavailable" in article["evidence_issues"]
    assert "Publication date is unavailable" in article["evidence_issues"]
    assert "Article content is unavailable" in article["evidence_issues"]


def test_invalid_url_marks_article_for_review():
    def fake_search(ticker, max_results=5):
        return {
            "provider": "Test provider",
            "articles": [
                {
                    "headline": "Company news",
                    "url": "not-a-url",
                    "source": "Example News",
                    "published_at": "2026-10-27",
                    "content": "Example article.",
                }
            ],
        }

    agent = VerifiedNewsAgent(news_search=fake_search)
    result = agent.analyse("AAPL")

    assert result["articles"][0]["evidence_status"] == "needs_review"


def test_search_error_is_preserved():
    def fake_search(ticker, max_results=5):
        return {
            "error": "The news search request failed.",
            "articles": [],
        }

    agent = VerifiedNewsAgent(news_search=fake_search)
    result = agent.analyse("AAPL")

    assert result["error"] == "The news search request failed."
    assert result["articles"] == []


def test_empty_ticker_is_rejected_without_search():
    def fake_search(ticker, max_results=5):
        raise AssertionError("Search should not be called")

    agent = VerifiedNewsAgent(news_search=fake_search)
    result = agent.analyse(" ")

    assert result["error"] == "Please provide a valid stock ticker."
    assert result["articles"] == []


def test_missing_publication_date():
    assert (
        VerifiedNewsAgent._publication_date_issue(None)
        == "Publication date is unavailable"
    )


def test_invalid_publication_date():
    assert (
        VerifiedNewsAgent._publication_date_issue("not-a-date")
        == "Publication date is invalid"
    )


def test_future_publication_date():
    from datetime import datetime, timedelta, timezone

    future_date = (
        datetime.now(timezone.utc) + timedelta(days=2)
    ).isoformat()

    assert (
        VerifiedNewsAgent._publication_date_issue(future_date)
        == "Publication date is in the future"
    )


def test_valid_tavily_publication_date():
    assert (
        VerifiedNewsAgent._publication_date_issue(
            "Wed, 28 Oct 2026 19:07:00 GMT"
        )
        is None
    )

def test_recent_article_is_fresh():
    from datetime import datetime, timedelta, timezone

    recent_date = (
        datetime.now(timezone.utc) - timedelta(days=2)
    ).isoformat()

    assert (
        VerifiedNewsAgent._freshness_status(recent_date)
        == "fresh"
    )


def test_old_article_is_stale():
    from datetime import datetime, timedelta, timezone

    old_date = (
        datetime.now(timezone.utc) - timedelta(days=10)
    ).isoformat()

    assert (
        VerifiedNewsAgent._freshness_status(old_date)
        == "stale"
    )


def test_missing_date_has_unknown_freshness():
    assert VerifiedNewsAgent._freshness_status(None) == "unknown"


def test_future_date_has_unknown_freshness():
    from datetime import datetime, timedelta, timezone

    future_date = (
        datetime.now(timezone.utc) + timedelta(days=2)
    ).isoformat()

    assert (
        VerifiedNewsAgent._freshness_status(future_date)
        == "unknown"
    )

def test_duplicate_url_is_flagged():
    def fake_search(ticker, max_results=5):
        article = {
            "headline": "Apple reports quarterly results",
            "url": "https://example.com/news#section",
            "source": "Example News",
            "published_at": "2026-10-27",
            "content": "Apple reported its quarterly results.",
        }
        duplicate = {
            **article,
            "url": "https://example.com/news",
            "headline": "A different headline for the same URL",
        }
        return {"provider": "Test", "articles": [article, duplicate]}

    result = VerifiedNewsAgent(news_search=fake_search).analyse("AAPL")

    assert result["articles"][0]["duplicate"] is False
    assert result["articles"][1]["duplicate"] is True
    assert "Duplicate URL" in result["articles"][1]["duplicate_reasons"]


def test_duplicate_headline_ignores_case_and_whitespace():
    def fake_search(ticker, max_results=5):
        base = {
            "url": "https://example.com/one",
            "source": "Example News",
            "published_at": "2026-10-27",
            "content": "Example content.",
        }
        return {
            "provider": "Test",
            "articles": [
                {**base, "headline": "Apple Reports Results"},
                {
                    **base,
                    "url": "https://example.com/two",
                    "headline": "  apple   reports results  ",
                },
            ],
        }

    result = VerifiedNewsAgent(news_search=fake_search).analyse("AAPL")

    assert result["articles"][1]["duplicate"] is True
    assert (
        "Duplicate headline"
        in result["articles"][1]["duplicate_reasons"]
    )


def test_duplicate_articles_are_preserved():
    def fake_search(ticker, max_results=5):
        article = {
            "headline": "Apple news",
            "url": "https://example.com/news",
            "source": "Example News",
            "published_at": "2026-10-27",
            "content": "Example content.",
        }
        return {
            "provider": "Test",
            "articles": [article, article.copy()],
        }

    result = VerifiedNewsAgent(news_search=fake_search).analyse("AAPL")

    assert len(result["articles"]) == 2
    assert result["articles"][1]["duplicate"] is True

