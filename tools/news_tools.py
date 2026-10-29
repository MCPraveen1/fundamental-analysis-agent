
"""Tools for retrieving financial news through Tavily."""

import os

import requests
from urllib.parse import urlparse
from dotenv import load_dotenv
from yfinance import ticker


load_dotenv()

TAVILY_SEARCH_URL = "https://api.tavily.com/search"


def search_financial_news(ticker: str, max_results: int = 5) -> dict:
    """Retrieve recent news search results for a stock ticker."""

    if not isinstance(ticker, str) or not ticker.strip():
        return {"error": "Please provide a valid stock ticker.", "articles": []}

    if not isinstance(max_results, int) or isinstance(max_results, bool):
        return {
            "error": "max_results must be an integer.",
            "articles": [],
        }

    if not 1 <= max_results <= 10:
        return {
            "error": "max_results must be between 1 and 10.",
            "articles": [],
        }

    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return {
            "error": "TAVILY_API_KEY is missing from the environment.",
            "articles": [],
        }

    ticker = ticker.strip().upper()

    payload = {
        "api_key": api_key,
        "query": f"{ticker} stock company financial news",
        "topic": "news",
        "max_results": max_results,
        "search_depth": "basic",
        "include_answer": False,
        "include_raw_content": False,
    }

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
            parsed_url = urlparse(article_url)
            hostname = parsed_url.hostname

            if hostname:
                source = hostname.removeprefix("www.")

        articles.append(
            {
                "headline": item.get("title"),
                "url": article_url,
                "source": source,
                "published_at": (
                    item.get("published_date")
                    or item.get("date")
                ),
                "content": item.get("content"),
                "relevance_score": item.get("score"),
            }
        )

    return {
        "ticker": ticker,
        "provider": "Tavily",
        "articles": articles,
    }
