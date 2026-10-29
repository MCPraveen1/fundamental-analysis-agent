
"""Evaluate the evidence quality of retrieved financial news."""

from urllib.parse import urlparse
from tools.news_tools import search_financial_news
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime


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
    
    @staticmethod
    def _publication_date_issue(published_at):
        """Return an issue message if the publication date is unusable."""

        if not isinstance(published_at, str) or not published_at.strip():
            return "Publication date is unavailable"

        try:
            publication_date = parsedate_to_datetime(published_at)
        except (TypeError, ValueError, OverflowError):
            try:
                publication_date = datetime.fromisoformat(
                    published_at.strip().replace("Z", "+00:00")
                )
            except (TypeError, ValueError, OverflowError):
                return "Publication date is invalid"

        if publication_date.tzinfo is None:
            publication_date = publication_date.replace(
                tzinfo=timezone.utc
            )

        if publication_date > datetime.now(timezone.utc):
            return "Publication date is in the future"

        return None

    
    @staticmethod
    def _freshness_status(published_at, max_age_days=7):
        """Classify an article by age without judging factual accuracy."""

        date_issue = VerifiedNewsAgent._publication_date_issue(
            published_at
        )

        if date_issue is not None:
            return "unknown"

        try:
            publication_date = parsedate_to_datetime(published_at)
        except (TypeError, ValueError, OverflowError):
            publication_date = datetime.fromisoformat(
                published_at.strip().replace("Z", "+00:00")
            )

        if publication_date.tzinfo is None:
            publication_date = publication_date.replace(
                tzinfo=timezone.utc
            )

        age = datetime.now(timezone.utc) - publication_date

        if age.days <= max_age_days:
            return "fresh"

        return "stale"


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
        seen_urls = set()
        seen_headlines = set()

        for article in result.get("articles", []):
            if not isinstance(article, dict):
                continue

            headline = article.get("headline")
            url = article.get("url")
            source = article.get("source")
            published_at = article.get("published_at")
            content = article.get("content")
            
            normalized_url = (
                urlparse(url.strip())._replace(fragment="").geturl().lower()
                if self._valid_http_url(url)
                else None
            )

            normalized_headline = (
                " ".join(headline.lower().split())
                if isinstance(headline, str) and headline.strip()
                else None
            )

            duplicate_reasons = []

            if normalized_url and normalized_url in seen_urls:
                duplicate_reasons.append("Duplicate URL")

            if (
                normalized_headline
                and normalized_headline in seen_headlines
            ):
                duplicate_reasons.append("Duplicate headline")

            if normalized_url:
                seen_urls.add(normalized_url)

            if normalized_headline:
                seen_headlines.add(normalized_headline)


            issues = []

            if not isinstance(headline, str) or not headline.strip():
                issues.append("Missing headline")

            if not self._valid_http_url(url):
                issues.append("Missing or invalid HTTP(S) URL")

            if not isinstance(source, str) or not source.strip():
                issues.append("Source is unavailable")

            date_issue = self._publication_date_issue(published_at)

            if date_issue:
              issues.append(date_issue)
            
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
                    "freshness_status": self._freshness_status(published_at),
                    "claims_independently_verified": False,
                    "duplicate": bool(duplicate_reasons),
                    "duplicate_reasons": duplicate_reasons,
                    
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
