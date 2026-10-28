
from tools.stock_data_router import get_stock_data


class LivePriceAgent:
    """Retrieve the latest available stock price from a data provider."""

    def analyse(self, ticker_symbol):
        """Return a structured result containing the available stock price."""

        if not isinstance(ticker_symbol, str) or not ticker_symbol.strip():
            return {"error": "Please provide a valid stock ticker."}

        ticker_symbol = ticker_symbol.strip().upper()
        snapshot = get_stock_data(ticker_symbol)

        if snapshot.get("error"):
            return {
                "ticker": ticker_symbol,
                "error": snapshot["error"],
            }

        current_price = snapshot.get("current_price")

        if current_price is None:
            return {
                "ticker": ticker_symbol,
                "error": "Current price is unavailable.",
                "data_source": snapshot.get("data_source"),
            }

        return {
            "ticker": snapshot.get("ticker", ticker_symbol),
            "company_name": snapshot.get("company_name"),
            "current_price": current_price,
            "currency": snapshot.get("currency"),
            "data_source": snapshot.get("data_source"),
        }
