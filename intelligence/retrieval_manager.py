
"""Coordinate curated-first and fallback financial news retrieval."""

from tools.news_tools import search_tavily
from intelligence.source_registry import get_sources_by_market
from intelligence.relevance_classifier import classify_article_relevance
from intelligence.article_deduplicator import deduplicate_articles


def retrieve_financial_news(
    identity: dict,
    search_plan: dict,
    max_results_per_query: int = 5,
    min_curated_articles: int = 2,
    min_category_articles: int = 1,
):
    """Retrieve, classify and deduplicate financial news."""

    if not isinstance(identity, dict):
        raise ValueError("Company identity must be a dictionary.")

    if not isinstance(search_plan, dict):
        raise ValueError("Search plan must be a dictionary.")

    market = identity.get("market")
    ticker = identity.get("ticker")

    if not market or not ticker:
        raise ValueError("Company identity is incomplete.")

    if not identity.get("company_name"):
        raise ValueError("Company identity must include company_name.")

    queries = search_plan.get("queries")

    if not isinstance(queries, list) or not queries:
        raise ValueError("Search plan must contain queries.")

    if (
        not isinstance(max_results_per_query, int)
        or isinstance(max_results_per_query, bool)
        or not 1 <= max_results_per_query <= 10
    ):
        raise ValueError("max_results_per_query must be between 1 and 10.")

    if (
        not isinstance(min_curated_articles, int)
        or isinstance(min_curated_articles, bool)
        or min_curated_articles < 1
    ):
        raise ValueError("min_curated_articles must be a positive integer.")

    if (
        not isinstance(min_category_articles, int)
        or isinstance(min_category_articles, bool)
        or min_category_articles < 1
    ):
        raise ValueError("min_category_articles must be a positive integer.")

    period_days = search_plan.get("period_days", 7)

    if (
        not isinstance(period_days, int)
        or isinstance(period_days, bool)
        or period_days < 1
    ):
        raise ValueError("period_days must be a positive integer.")

    sources = get_sources_by_market(market)
    curated_domains = [source["domain"] for source in sources]

    relevant_articles = []
    rejected_articles = []

    def process_articles(raw_articles, category, retrieval_tier):
        """Classify articles and retain their retrieval metadata."""

        accepted = []

        for article in raw_articles:
            if not isinstance(article, dict):
                continue

            classification = classify_article_relevance(
                article,
                identity,
            )

            enriched_article = {
                **article,
                "category": category,
                "retrieval_tier": retrieval_tier,
                **classification,
            }

            if classification["is_relevant"]:
                accepted.append(enriched_article)
            else:
                rejected_articles.append({
                    **enriched_article,
                    "rejection_reason": (
                        "Article did not meet the company and "
                        "financial-category relevance criteria."
                    ),
                })

        return accepted

    valid_queries = [
        item
        for item in queries
        if isinstance(item, dict)
        and item.get("category")
        and item.get("query")
    ]

    # Stage 1: Search curated publishers.
    for query_item in valid_queries:
        category = query_item["category"]

        result = search_tavily(
            query=query_item["query"],
            max_results=max_results_per_query,
            include_domains=curated_domains,
            days=period_days,
        )

        raw_articles = result.get("articles", [])

        if result.get("error") or not isinstance(raw_articles, list):
            raw_articles = []

        accepted = process_articles(
            raw_articles,
            category,
            "curated",
        )

        relevant_articles.extend(accepted)

    # Stage 2: Deduplicate curated results before measuring coverage.
    curated_articles = deduplicate_articles(relevant_articles)

    curated_count = len(curated_articles)

    category_counts = {
        item["category"]: sum(
            1
            for article in curated_articles
            if item["category"] in article.get("matched_categories", [])
        )
        for item in valid_queries
    }

    # Stage 3: Identify categories needing additional coverage.
    fallback_categories = [
        item
        for item in valid_queries
        if category_counts.get(item["category"], 0)
        < min_category_articles
    ]

    if curated_count < min_curated_articles:
        fallback_categories = valid_queries.copy()

    # Stage 4: Search broader sources where needed.
    for query_item in fallback_categories:
        category = query_item["category"]

        result = search_tavily(
            query=query_item["query"],
            max_results=max_results_per_query,
            days=period_days,
        )

        raw_articles = result.get("articles", [])

        if result.get("error") or not isinstance(raw_articles, list):
            raw_articles = []

        accepted = process_articles(
            raw_articles,
            category,
            "fallback",
        )

        relevant_articles.extend(accepted)

    # Stage 5: Deduplicate the combined curated and fallback results.
    unique_articles = deduplicate_articles(relevant_articles)

    return {
        "ticker": ticker,
        "market": market,
        "period_days": period_days,
        "curated_domains": curated_domains,
        "articles": unique_articles,
        "rejected_articles": rejected_articles,
        "curated_article_count": curated_count,
        "category_counts": category_counts,
        "fallback_categories": [
            item["category"] for item in fallback_categories
        ],
        "total_unique_articles": len(unique_articles),
    }
