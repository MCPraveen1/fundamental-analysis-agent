
"""Deduplicate financial news articles while preserving provenance."""

import re
from urllib.parse import (
    parse_qsl,
    urlencode,
    urlsplit,
    urlunsplit,
)


TRACKING_PARAMETERS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "fbclid",
    "gclid",
}


def normalize_headline(headline):
    """Normalize headlines for duplicate comparison."""

    if not isinstance(headline, str):
        return ""

    headline = headline.lower()
    headline = re.sub(r"[^\w\s]", "", headline)
    headline = re.sub(r"\s+", " ", headline)

    return headline.strip()


def normalize_url(url):
    """Normalize URLs by removing fragments and tracking parameters."""

    if not isinstance(url, str) or not url.strip():
        return ""

    try:
        parsed = urlsplit(url.strip())

        if parsed.scheme.lower() not in {"http", "https"}:
            return ""

        if not parsed.hostname:
            return ""

        scheme = parsed.scheme.lower()
        hostname = parsed.hostname.lower().removeprefix("www.")

        port = parsed.port
        if port and not (
            (scheme == "http" and port == 80)
            or (scheme == "https" and port == 443)
        ):
            hostname = f"{hostname}:{port}"

        path = parsed.path.rstrip("/")

        query_parameters = [
            (key, value)
            for key, value in parse_qsl(
                parsed.query,
                keep_blank_values=True,
            )
            if key.lower() not in TRACKING_PARAMETERS
        ]

        query = urlencode(sorted(query_parameters))

        return urlunsplit((
            scheme,
            hostname,
            path,
            query,
            "",
        ))

    except ValueError:
        return ""


def deduplicate_articles(articles):
    """Remove duplicate articles and preserve their retrieval provenance."""

    if not isinstance(articles, list):
        raise ValueError("Articles must be provided as a list.")

    unique_articles = []
    seen_by_url = {}
    seen_by_headline = {}

    for article in articles:
        if not isinstance(article, dict):
            continue

        headline = article.get("headline", "")
        normalized_headline = normalize_headline(headline)
        normalized_url = normalize_url(article.get("url"))

        if not normalized_headline and not normalized_url:
            continue

        existing_index = None

        if normalized_url:
            existing_index = seen_by_url.get(normalized_url)

        if (
            existing_index is None
            and normalized_headline
        ):
            existing_index = seen_by_headline.get(
                normalized_headline
            )

        if existing_index is not None:
            existing = unique_articles[existing_index]

            # Preserve all retrieval tiers.
            tiers = set(existing.get("retrieval_tiers", []))
            tiers.update(
                existing.get("retrieval_tier")
                for _ in [0]
                if existing.get("retrieval_tier")
            )
            if article.get("retrieval_tier"):
                tiers.add(article["retrieval_tier"])

            existing["retrieval_tiers"] = sorted(tiers)

            # Preserve categories discovered through different searches.
            categories = set(existing.get("retrieval_categories", []))
            if existing.get("category"):
                categories.add(existing["category"])
            if article.get("category"):
                categories.add(article["category"])

            existing["retrieval_categories"] = sorted(categories)

            # Preserve independently identified financial categories.
            matched_categories = set(
                existing.get("matched_categories", [])
            )
            matched_categories.update(
                article.get("matched_categories", [])
            )
            existing["matched_categories"] = sorted(
                matched_categories
            )

            # Preserve alternate article URLs.
            alternate_urls = set(existing.get("alternate_urls", []))
            if article.get("url") and article["url"] != existing.get("url"):
                alternate_urls.add(article["url"])

            existing["alternate_urls"] = sorted(alternate_urls)

            # Register new identifiers against the retained article.
            if normalized_url:
                seen_by_url[normalized_url] = existing_index

            if normalized_headline:
                seen_by_headline[normalized_headline] = existing_index

            continue

        retained_article = dict(article)

        retained_article["retrieval_tiers"] = (
            [article["retrieval_tier"]]
            if article.get("retrieval_tier")
            else []
        )

        retained_article["retrieval_categories"] = (
            [article["category"]]
            if article.get("category")
            else []
        )

        retained_article["alternate_urls"] = []

        unique_index = len(unique_articles)
        unique_articles.append(retained_article)

        if normalized_url:
            seen_by_url[normalized_url] = unique_index

        if normalized_headline:
            seen_by_headline[normalized_headline] = unique_index

    return unique_articles
