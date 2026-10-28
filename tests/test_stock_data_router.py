
from tools.stock_data_router import get_stock_data


def test_fmp_normalization_includes_quote_when_available(monkeypatch):
    """Preserve price and currency when FMP supplies quote data."""

    monkeypatch.setattr(
        "tools.stock_data_router.get_fmp_financials",
        lambda symbol: {
            "company_profile": {
                "companyName": "Apple Inc.",
                "currency": "USD",
                "price": 225.50,
            },
            "income_statement": [],
            "balance_sheet": [],
            "cash_flow_statement": [],
        },
    )

    result = get_stock_data("AAPL")

    assert result["ticker"] == "AAPL"
    assert result["currency"] == "USD"
    assert result["current_price"] == 225.50


def test_fmp_normalization_handles_missing_price(monkeypatch):
    """Do not invent a price when FMP provides none."""

    monkeypatch.setattr(
        "tools.stock_data_router.get_fmp_financials",
        lambda symbol: {
            "company_profile": {
                "companyName": "Apple Inc.",
                "currency": "USD",
            },
            "income_statement": [],
            "balance_sheet": [],
            "cash_flow_statement": [],
        },
    )

    result = get_stock_data("AAPL")

    assert result["current_price"] is None
