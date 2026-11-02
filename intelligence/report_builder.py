
"""Build structured financial intelligence reports from assessed news."""

REPORT_CATEGORIES = (
    "company_developments",
    "financial_performance",
    "market_reaction",
    "expert_analysis",
)

EVIDENCE_TYPES = (
    "primary_source_statement",
    "reported_fact",
    "analyst_opinion",
    "forecast",
    "unverified_claim",
)


def build_financial_intelligence_report(news_analysis):
    """Build a structured report from VerifiedNewsAgent output."""

    if not isinstance(news_analysis, dict):
        raise ValueError("News analysis must be a dictionary.")

    if news_analysis.get("error"):
        raise ValueError(
            "Cannot build a report from failed news analysis."
        )

    ticker = news_analysis.get("ticker")

    if not ticker:
        raise ValueError("News analysis must contain a ticker.")

    articles = news_analysis.get("articles", [])

    if not isinstance(articles, list):
        raise ValueError("Articles must be provided as a list.")

    # Group articles by their matched financial categories.
    categorized_articles = {
        category: [] for category in REPORT_CATEGORIES
    }

    for article in articles:
        if not isinstance(article, dict):
            continue

        matched_categories = article.get("matched_categories", [])

        if not isinstance(matched_categories, list):
            matched_categories = []

        # Retain compatibility with articles containing only category.
        category = article.get("category")

        if category and category not in matched_categories:
            matched_categories.append(category)

        for matched_category in dict.fromkeys(matched_categories):
            if matched_category in categorized_articles:
                categorized_articles[matched_category].append(article)

    # Count evidence classifications.
    evidence_counts = {
        evidence_type: 0
        for evidence_type in EVIDENCE_TYPES
    }

    for article in articles:
        if not isinstance(article, dict):
            continue

        evidence_type = article.get("evidence_type")

        if evidence_type in evidence_counts:
            evidence_counts[evidence_type] += 1

    # Assess source provenance.
    primary_source_count = 0
    secondary_source_count = 0
    verified_source_count = 0
    unknown_source_count = 0

    for article in articles:
        if not isinstance(article, dict):
            continue

        source_type = article.get("source_type")

        if source_type == "primary_source":
            primary_source_count += 1
        elif source_type in {
            "financial_news",
            "investment_analysis",
        }:
            secondary_source_count += 1
        else:
            unknown_source_count += 1

        if article.get("source_verified") is True:
            verified_source_count += 1

    # Identify article metadata limitations.
    metadata_incomplete_count = sum(
        1
        for article in articles
        if isinstance(article, dict)
        and article.get("evidence_status") != "metadata_complete"
    )

    verification_required_count = sum(
        1
        for article in articles
        if isinstance(article, dict)
        and article.get("requires_verification") is True
    )

    rejected_articles = news_analysis.get("rejected_articles", [])
    search_errors = news_analysis.get("search_errors", [])

    if not isinstance(rejected_articles, list):
        rejected_articles = []

    if not isinstance(search_errors, list):
        search_errors = []

    category_counts = news_analysis.get("category_counts", {})

    if not isinstance(category_counts, dict):
        category_counts = {}

    # Build transparent report limitations.
    limitations = []

    if not articles:
        limitations.append("No relevant articles were retrieved.")

    if search_errors:
        limitations.append(
            f"{len(search_errors)} search operation(s) failed."
        )

    if rejected_articles:
        limitations.append(
            f"{len(rejected_articles)} article(s) were rejected "
            "by relevance classification."
        )

    if metadata_incomplete_count:
        limitations.append(
            f"{metadata_incomplete_count} article(s) have incomplete "
            "or invalid metadata."
        )

    if verification_required_count:
        limitations.append(
            f"{verification_required_count} article(s) require "
            "additional claim verification."
        )

    if unknown_source_count:
        limitations.append(
            f"{unknown_source_count} article(s) have no confirmed "
            "primary/secondary source classification."
        )

    search_plan = news_analysis.get("search_plan")

    if not isinstance(search_plan, dict):
        search_plan = {}
    return {"report_type": "financial_intelligence",
            "ticker": ticker,
            "company": news_analysis.get("company_identity", {}),
            "period_days": search_plan.get("period_days", 7),
            "retrieval_summary": {
                "total_unique_articles": news_analysis.get(
                    "total_unique_articles", len(articles)
                ),
            "curated_article_count": news_analysis.get(
                "curated_article_count", 0
            ),
            "rejected_article_count": len(rejected_articles),
            "search_error_count": len(search_errors),
            "category_counts": category_counts,
            "fallback_categories": news_analysis.get(
                "fallback_categories", []
            ),
        },
        "news_categories": categorized_articles,
        "evidence_summary": {
            "evidence_type_counts": evidence_counts,
            "verification_required_count": verification_required_count,
            "claims_independently_verified": False,
        },
        "source_quality": {
            "primary_source_count": primary_source_count,
            "secondary_source_count": secondary_source_count,
            "verified_publisher_count": verified_source_count,
            "unknown_source_count": unknown_source_count,
        },
        "limitations": limitations,
        "rejected_articles": rejected_articles,
        "search_errors": search_errors,
        "verification_note": news_analysis.get(
            "verification_note",
            "Source registration and metadata completeness "
            "do not establish factual accuracy.",
        ),
    }
