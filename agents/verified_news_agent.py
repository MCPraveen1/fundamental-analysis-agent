
"""Evaluate the evidence quality of retrieved financial news."""

from urllib.parse import urlparse

from tools.news_tools import search_financial_news


class VerifiedNewsAgent:
    """Assess news metadata without claiming to verify factual truth."""

    def __init__(self, news_search=None):
        self.news_search = news_search or search_financial_news

    @staticmethod
    def _valid_http_url(url):
        """Return whether a URL has a valid HTTP(S) structure."""
        if not isinstance(url, str) or not url.strip():
            return False

        try:
            parsed = urlparse(url.strip())
            return (
                parsed.scheme in {"http", "https"}
                and bool(parsed.netloc)
                and "." in parsed.netloc
            )
        except ValueError:
            return False

    def analyse(self, ticker, max_results=5):
        """Retrieve news and assess the completeness of each article."""

        if not isinstance(ticker, str) or not ticker.strip():
            return {
                "ticker": ticker,
                "error": "Please provide a valid stock ticker.",
                "articles": [],
            }

        result = self.news_search(ticker, max_results=max_results)

        if result.get("error"):
            return {
                "ticker": ticker.strip().upper(),
                "error": result["error"],
                "articles": [],
            }

        assessed_articles = []

        for article in result.get("articles", []):
            if not isinstance(article, dict):
                continue

            headline = article.get("headline")
            url = article.get("url")
            source = article.get("source")
            published_at = article.get("published_at")
            content = article.get("content")

            issues = []

            if not isinstance(headline, str) or not headline.strip():
                issues.append("Missing headline")

            if not self._valid_http_url(url):
                issues.append("Missing or invalid HTTP(S) URL")

            if not isinstance(source, str) or not source.strip():
                issues.append("Source is unavailable")

            if not published_at:
                issues.append("Publication date is unavailable")

            if not isinstance(content, str) or not content.strip():
                issues.append("Article content is unavailable")

            if any(
                issue in issues
                for issue in (
                    "Missing headline",
                    "Missing or invalid HTTP(S) URL",
                )
            ):
                status = "needs_review"
            elif issues:
                status = "incomplete"
            else:
                status = "metadata_complete"

            assessed_articles.append(
                {
                    **article,
                    "evidence_status": status,
                    "evidence_issues": issues,
                    "claims_independently_verified": False,
                }
            )

        return {
            "ticker": ticker.strip().upper(),
            "provider": result.get("provider"),
            "articles": assessed_articles,
            "verification_note": (
                "Metadata completeness does not establish the truth "
                "of an article's claims."
            ),
        }
