
"""Rule-based relevance classification for financial news articles."""

import re


CATEGORY_KEYWORDS = {
    "company_developments": {
        "announcement", "acquisition", "investment", "expansion",
        "partnership", "merger", "launch", "divestment", "subsidiary",
        "contract", "approval", "regulatory", "project",
    },
    "financial_performance": {
        "revenue", "profit", "earnings", "ebitda", "margin",
        "financial results", "quarterly results", "net income",
        "cash flow", "debt", "loss", "guidance",
    },
    "market_reaction": {
        "share price", "stock price", "shares", "trading volume",
        "market reaction", "surged", "fell", "declined", "rallied",
        "market capitalization", "valuation",
    },
    "expert_analysis": {
        "analyst", "brokerage", "price target", "rating",
        "upgrade", "downgrade", "recommendation", "outlook",
        "forecast", "valuation", "research report",
    },
}


def normalize_text(value):
    """Normalize text for consistent keyword matching."""
    if not isinstance(value, str):
        return ""

    return re.sub(r"\s+", " ", value.lower()).strip()



def contains_company_reference(text, company_name, ticker):
    """Check company references using full and shortened company names."""
    normalized_text = normalize_text(text)
    normalized_name = normalize_text(company_name)
    normalized_ticker = normalize_text(ticker)

    # Remove common legal entity suffixes.
    legal_suffixes = {
        "limited", "ltd", "inc", "incorporated",
        "corporation", "corp", "plc", "llc",
    }

    name_words = normalized_name.split()

    while name_words and name_words[-1].rstrip(".") in legal_suffixes:
        name_words.pop()

    name_variants = set()

    if normalized_name:
        name_variants.add(normalized_name)

    if name_words:
        name_variants.add(" ".join(name_words))

        # Common shortened company name used in news headlines.
        name_variants.add(name_words[0])

    name_found = any(
        re.search(
            r"(?<![a-z0-9])" + re.escape(variant) + r"(?![a-z0-9])",
            normalized_text,
        )
        for variant in name_variants
        if variant
    )

    ticker_found = False

    if normalized_ticker:
        ticker_pattern = (
            r"(?<![A-Za-z0-9])"
            + re.escape(normalized_ticker)
            + r"(?![A-Za-z0-9])"
        )
        ticker_found = bool(
            re.search(ticker_pattern, text, re.IGNORECASE)
        )

    return name_found or ticker_found



def classify_article_relevance(article, identity):
    """Classify company relevance and financial-analysis category relevance."""

    if not isinstance(article, dict):
        raise ValueError("Article must be a dictionary.")

    if not isinstance(identity, dict):
        raise ValueError("Company identity must be a dictionary.")

    company_name = identity.get("company_name")
    ticker = identity.get("ticker")

    if not company_name or not ticker:
        raise ValueError("Company identity must include name and ticker.")

    headline = article.get("headline", "")
    content = article.get("content", "")

    headline_text = normalize_text(headline)
    content_text = normalize_text(content)
    combined_text = f"{headline_text} {content_text}"

    headline_match = contains_company_reference(
        headline, company_name, ticker
    )
    content_match = contains_company_reference(
        content, company_name, ticker
    )

    if headline_match:
        company_relevance = "direct"
    elif content_match:
        company_relevance = "mention"
    else:
        company_relevance = "unrelated"

    matched_categories = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(
            keyword in combined_text
            for keyword in keywords
        ):
            matched_categories.append(category)

    is_relevant = (
        company_relevance == "direct"
        and bool(matched_categories)
    )

    return {
        "company_relevance": company_relevance,
        "matched_categories": matched_categories,
        "is_relevant": is_relevant,
    }
