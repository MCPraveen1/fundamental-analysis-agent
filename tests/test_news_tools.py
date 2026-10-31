
import requests
from unittest.mock import Mock, patch
from tools.news_tools import search_financial_news, search_tavily



def test_empty_ticker_is_rejected():
    result = search_financial_news(" ")

    assert result["error"] == "Please provide a valid stock ticker."
    assert result["articles"] == []


def test_invalid_max_results_is_rejected():
    result = search_financial_news("AAPL", max_results=0)

    assert result["error"] == "max_results must be between 1 and 10."
    assert result["articles"] == []


def test_non_integer_max_results_is_rejected():
    result = search_financial_news("AAPL", max_results="5")

    assert result["error"] == "max_results must be an integer."
    assert result["articles"] == []


@patch("tools.news_tools.requests.post")
@patch("tools.news_tools.os.getenv")
def test_successful_news_search(mock_getenv, mock_post):
    mock_getenv.return_value = "test-api-key"

    mock_response = Mock()
    mock_response.json.return_value = {
        "results": [
            {
                "title": "Example company earnings news",
                "url": "https://example.com/news",
                "source": "Example News",
                "published_date": "2026-10-27",
                "content": "Example news content.",
                "score": 0.95,
            }
        ]
    }
    mock_post.return_value = mock_response

    result = search_financial_news("aapl")

    assert result["ticker"] == "AAPL"
    assert result["provider"] == "Tavily"
    assert len(result["articles"]) == 1
    assert result["articles"][0]["headline"] == (
        "Example company earnings news"
    )
    assert result["articles"][0]["url"] == "https://example.com/news"
    assert result["articles"][0]["published_at"] == "2026-10-27"

    mock_post.assert_called_once()
    mock_response.raise_for_status.assert_called_once()


@patch("tools.news_tools.requests.post")
@patch("tools.news_tools.os.getenv")
def test_news_search_timeout(mock_getenv, mock_post):
    mock_getenv.return_value = "test-api-key"
    mock_post.side_effect = requests.Timeout

    result = search_financial_news("AAPL")

    assert result["error"] == "The news search request timed out."
    assert result["articles"] == []


@patch("tools.news_tools.requests.post")
@patch("tools.news_tools.os.getenv")
def test_missing_api_key_does_not_make_request(mock_getenv, mock_post):
    mock_getenv.return_value = None

    result = search_financial_news("AAPL")

    assert result["error"] == (
        "TAVILY_API_KEY is missing from the environment."
    )
    assert result["articles"] == []
    mock_post.assert_not_called()


@patch("tools.news_tools.requests.post")
@patch("tools.news_tools.os.getenv")
def test_news_search_http_error(mock_getenv, mock_post):
    mock_getenv.return_value = "test-api-key"
    mock_post.side_effect = requests.HTTPError("HTTP 401")

    result = search_financial_news("AAPL")

    assert result["error"] == "The news search request failed."
    assert result["articles"] == []


@patch("tools.news_tools.requests.post")
@patch("tools.news_tools.os.getenv")
def test_news_search_invalid_json(mock_getenv, mock_post):
    mock_getenv.return_value = "test-api-key"

    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_post.return_value = mock_response

    result = search_financial_news("AAPL")

    assert result["error"] == "The news provider returned invalid JSON."
    assert result["articles"] == []


@patch("tools.news_tools.requests.post")
@patch("tools.news_tools.os.getenv")
def test_curated_search_passes_domains_and_days(mock_getenv, mock_post):
    mock_getenv.return_value = "test-api-key"

    mock_response = Mock()
    mock_response.json.return_value = {"results": []}
    mock_post.return_value = mock_response

    result = search_tavily(
        query="Reliance Industries financial results",
        max_results=5,
        include_domains=["reuters.com", "livemint.com"],
        days=7,
    )

    assert result["provider"] == "Tavily"
    assert result["articles"] == []

    payload = mock_post.call_args.kwargs["json"]

    assert payload["query"] == "Reliance Industries financial results"
    assert payload["include_domains"] == [
        "reuters.com",
        "livemint.com",
    ]
    assert payload["days"] == 7


@patch("tools.news_tools.requests.post")
@patch("tools.news_tools.os.getenv")
def test_fallback_search_does_not_restrict_domains(mock_getenv, mock_post):
    mock_getenv.return_value = "test-api-key"

    mock_response = Mock()
    mock_response.json.return_value = {"results": []}
    mock_post.return_value = mock_response

    search_tavily(
        query="Reliance Industries financial results",
        days=7,
    )

    payload = mock_post.call_args.kwargs["json"]

    assert "include_domains" not in payload
    assert payload["days"] == 7


def test_invalid_days_is_rejected():
    result = search_tavily(
        query="Reliance Industries",
        days=0,
    )

    assert result["error"] == "days must be a positive integer."
    assert result["articles"] == []


def test_non_integer_days_is_rejected():
    result = search_tavily(
        query="Reliance Industries",
        days="7",
    )

    assert result["error"] == "days must be a positive integer."
    assert result["articles"] == []


def test_invalid_include_domains_is_rejected():
    result = search_tavily(
        query="Reliance Industries",
        include_domains="reuters.com",
    )

    assert result["error"] == (
        "include_domains must be a list of valid domains."
    )
    assert result["articles"] == []

