from unittest.mock import patch

from intelligence.identity_resolver import resolve_company_identity


@patch("intelligence.identity_resolver.get_stock_data")
def test_resolve_indian_company(mock_get_stock_data):
    mock_get_stock_data.return_value = {
        "company_name": "Reliance Industries Limited",
        "currency": "INR",
        "data_source": "Yahoo Finance via yfinance",
        "error": None,
    }

    result = resolve_company_identity("RELIANCE.NS")

    assert result["ticker"] == "RELIANCE.NS"
    assert result["company_name"] == "Reliance Industries Limited"
    assert result["market"] == "INDIA"
    assert result["exchange"] == "NSE"
    assert result["currency"] == "INR"


@patch("intelligence.identity_resolver.get_stock_data")
def test_resolve_us_company(mock_get_stock_data):
    mock_get_stock_data.return_value = {
        "company_name": "Apple Inc.",
        "currency": "USD",
        "data_source": "Financial Modeling Prep",
        "error": None,
    }

    result = resolve_company_identity("AAPL")

    assert result["ticker"] == "AAPL"
    assert result["company_name"] == "Apple Inc."
    assert result["market"] == "US"
    assert result["exchange"] == "US_MARKET"
    assert result["currency"] == "USD"


def test_empty_ticker_is_rejected():
    result = resolve_company_identity(" ")

    assert result["error"] == "Please provide a valid stock ticker."


@patch("intelligence.identity_resolver.get_stock_data")
def test_stock_data_error_is_returned(mock_get_stock_data):
    mock_get_stock_data.return_value = {
        "error": "Unable to retrieve stock data."
    }

    result = resolve_company_identity("AAPL")

    assert result["ticker"] == "AAPL"
    assert result["error"] == "Unable to retrieve stock data."


@patch("intelligence.identity_resolver.get_stock_data")
def test_ticker_is_normalized(mock_get_stock_data):
    mock_get_stock_data.return_value = {
        "company_name": "Reliance Industries Limited",
        "currency": "INR",
        "data_source": "Yahoo Finance via yfinance",
        "error": None,
    }

    result = resolve_company_identity(" reliance.ns ")

    assert result["ticker"] == "RELIANCE.NS"
    mock_get_stock_data.assert_called_once_with("RELIANCE.NS")