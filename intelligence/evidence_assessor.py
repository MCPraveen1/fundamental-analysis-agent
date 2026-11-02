
"""Classify financial news evidence by its source and claim type."""

import re
from intelligence.source_registry import resolve_article_source

PRIMARY_SOURCE_KEYWORDS = {
    "investor relations",
    "press release",
    "official announcement",
    "company filing",
    "exchange filing",
    "annual report",
    "quarterly report",
    "regulatory filing",
}

ANALYST_KEYWORDS = {
    "analyst",
    "brokerage",
    "research report",
    "price target",
    "rating",
    "upgrade",
    "downgrade",
    "buy recommendation",
    "sell recommendation",
}

FORECAST_KEYWORDS = {
    "forecast",
    "expects",
    "expected to",
    "projected",
    "projection",
    "outlook",
    "target price",
    "estimated to",
    "could reach",
    "may increase",
    "may decline",
    "guidance",
}

REPORTED_FACT_KEYWORDS = {
    "reported",
    "announced",
    "recorded",
    "posted",
    "revenue",
    "profit",
    "earnings",
    "ebitda",
    "net income",
    "cash flow",
    "debt",
    "financial results",
}


def normalize_text(value):
    """Normalize text for consistent evidence keyword matching."""

    if not isinstance(value, str):
        return ""

    return re.sub(r"\s+", " ", value.lower()).strip()


def assess_evidence(article):
    """Classify the evidence type of a financial news article."""

    if not isinstance(article, dict):
        raise ValueError("Article must be a dictionary.")

    headline = normalize_text(article.get("headline", ""))
    content = normalize_text(article.get("content", ""))
    source_provenance = resolve_article_source(
        article.get("url")
)

    combined_text = f"{headline} {content}"

    if not combined_text.strip():
        return {
            "evidence_type": "unverified_claim",
            "evidence_basis": "No article content available.",
            "is_forecast": False,
            "requires_verification": True,
            **source_provenance,
        }

    # Identify primary-source indicators.
    primary_source_match = any(
        keyword in combined_text
        for keyword in PRIMARY_SOURCE_KEYWORDS
    )

    # Identify analyst-related indicators.
    analyst_match = any(
        keyword in combined_text
        for keyword in ANALYST_KEYWORDS
    )

    # Identify forward-looking statements.
    forecast_match = any(
        keyword in combined_text
        for keyword in FORECAST_KEYWORDS
    )

    # Identify reported financial facts.
    reported_fact_match = any(
        keyword in combined_text
        for keyword in REPORTED_FACT_KEYWORDS
    )

        # Determine the evidence classification.
    if forecast_match and analyst_match:
        evidence_type = "forecast"
        evidence_basis = "Analyst-related forward-looking statement."

    elif forecast_match:
        evidence_type = "forecast"
        evidence_basis = "Forward-looking statement detected."

    elif analyst_match:
        evidence_type = "analyst_opinion"
        evidence_basis = "Analyst or brokerage-related statement detected."

    elif primary_source_match:
        evidence_type = "primary_source_statement"
        evidence_basis = "Primary-source language detected in article."

    elif reported_fact_match:
        evidence_type = "reported_fact"
        evidence_basis = "Reported financial information detected."

    else:
        evidence_type = "unverified_claim"
        evidence_basis = "Insufficient evidence indicators detected."

    return {
        "evidence_type": evidence_type,
        "evidence_basis": evidence_basis,
        "is_forecast": evidence_type == "forecast",
        "requires_verification": (
            evidence_type == "unverified_claim"
        ),
        **source_provenance,
    }