from tools.stock_data_router import get_stock_data


def resolve_company_identity(ticker):
    """Resolve a ticker into company identity and market information."""

    if not isinstance(ticker, str) or not ticker.strip():
        return {
            "error": "Please provide a valid stock ticker."
        }

    ticker = ticker.strip().upper()

    stock_data = get_stock_data(ticker)

    if stock_data.get("error"):
        return {
            "ticker": ticker,
            "error": stock_data["error"],
        }

    if ticker.endswith((".NS", ".BO")):
        market = "INDIA"
        exchange = "NSE" if ticker.endswith(".NS") else "BSE"
    else:
        market = "US"
        exchange = "US_MARKET"

    return {
        "ticker": ticker,
        "company_name": stock_data.get("company_name"),
        "market": market,
        "exchange": exchange,
        "currency": stock_data.get("currency"),
        "data_source": stock_data.get("data_source"),
    }