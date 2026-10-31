
"""Tools for retrieving financial news through Tavily."""

import os
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv


load_dotenv()

TAVILY_SEARCH_URL = "https://api.tavily.com/search"


def search_tavily(
    query: str,
    max_results: int = 5,
    include_domains: list[str] | None = None,
    days: int = 7,
) -> dict:
    """Search Tavily for recent financial news."""

    if not isinstance(query, str) or not query.strip():
        return {"error": "Please provide a valid search query.", "articles": []}

    if not isinstance(max_results, int) or isinstance(max_results, bool):
        return {"error": "max_results must be an integer.", "articles": []}

    if not 1 <= max_results <= 10:
        return {
            "error": "max_results must be between 1 and 10.",
            "articles": [],
        }

    if not isinstance(days, int) or isinstance(days, bool) or days < 1:
        return {"error": "days must be a positive integer.", "articles": []}

    if include_domains is not None:
        if (
            not isinstance(include_domains, list)
            or not all(
                isinstance(domain, str) and domain.strip()
                for domain in include_domains
            )
        ):
            return {
                "error": "include_domains must be a list of valid domains.",
                "articles": [],
            }

    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return {
            "error": "TAVILY_API_KEY is missing from the environment.",
            "articles": [],
        }

    payload = {
        "api_key": api_key,
        "query": query.strip(),
        "topic": "news",
        "max_results": max_results,
        "search_depth": "basic",
        "days": days,
        "include_answer": False,
        "include_raw_content": False,
    }

    if include_domains:
        payload["include_domains"] = include_domains

    try:
        response = requests.post(
            TAVILY_SEARCH_URL,
            json=payload,
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()

    except requests.Timeout:
        return {
            "error": "The news search request timed out.",
            "articles": [],
        }
    except requests.RequestException:
        return {
            "error": "The news search request failed.",
            "articles": [],
        }
    except ValueError:
        return {
            "error": "The news provider returned invalid JSON.",
            "articles": [],
        }

    if not isinstance(data, dict):
        return {
            "error": "The news provider returned an unexpected response.",
            "articles": [],
        }

    results = data.get("results", [])

    if not isinstance(results, list):
        return {
            "error": "The news provider returned an unexpected result format.",
            "articles": [],
        }

    articles = []

    for item in results:
        if not isinstance(item, dict):
            continue

        article_url = item.get("url")
        source = item.get("source")

        if not source and isinstance(article_url, str):
            hostname = urlparse(article_url).hostname
            if hostname:
                source = hostname.removeprefix("www.")

        articles.append(
            {
                "headline": item.get("title"),
                "url": article_url,
                "source": source,
                "published_at": (
                    item.get("published_date") or item.get("date")
                ),
                "content": item.get("content"),
                "relevance_score": item.get("score"),
            }
        )

    return {
        "provider": "Tavily",
        "articles": articles,
    }


def search_financial_news(ticker: str, max_results: int = 5) -> dict:
    """Compatibility wrapper for the existing news search interface."""

    if not isinstance(ticker, str) or not ticker.strip():
        return {"error": "Please provide a valid stock ticker.", "articles": []}

    normalized_ticker = ticker.strip().upper()

    result = search_tavily(
        query=f"{normalized_ticker} stock company financial news",
        max_results=max_results,
    )

    return {
        **result,
        "ticker": normalized_ticker,
    }
