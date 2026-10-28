
from agents.live_price_agent import LivePriceAgent


def test_returns_available_stock_price(monkeypatch):
    """Return price and metadata from the provider."""

    monkeypatch.setattr(
        "agents.live_price_agent.get_stock_data",
        lambda ticker: {
            "ticker": ticker,
            "company_name": "Reliance Industries Limited",
            "current_price": 1450.50,
            "currency": "INR",
            "data_source": "Yahoo Finance via yfinance",
        },
    )

    result = LivePriceAgent().analyse("reliance.ns")

    assert result["ticker"] == "RELIANCE.NS"
    assert result["current_price"] == 1450.50
    assert result["currency"] == "INR"


def test_handles_unavailable_price(monkeypatch):
    """Return a clear error when the price is missing."""

    monkeypatch.setattr(
        "agents.live_price_agent.get_stock_data",
        lambda ticker: {
            "ticker": ticker,
            "current_price": None,
            "data_source": "Yahoo Finance via yfinance",
        },
    )

    result = LivePriceAgent().analyse("RELIANCE.NS")

    assert result["error"] == "Current price is unavailable."


def test_handles_provider_error(monkeypatch):
    """Pass provider errors through to the result."""

    monkeypatch.setattr(
        "agents.live_price_agent.get_stock_data",
        lambda ticker: {"error": "Provider unavailable"},
    )

    result = LivePriceAgent().analyse("AAPL")

    assert result["error"] == "Provider unavailable"


def test_rejects_empty_ticker():
    """Reject empty input without fetching data."""

    result = LivePriceAgent().analyse("  ")

    assert result["error"] == "Please provide a valid stock ticker."
