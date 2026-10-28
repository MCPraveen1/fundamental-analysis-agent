
from tools.financial_tools import get_stock_snapshot
from tools.fmp_tools import get_fmp_financials


def _normalize_stock_data(symbol, provider, raw_data):
    """Return a consistent top-level structure for either provider."""

    if raw_data.get("error"):
        return {
            "ticker": symbol,
            "company_name": None,
            "currency": None,
            "financials": {},
            "history": {},
            "data_source": provider,
            "error": raw_data["error"],
            "raw_data": raw_data,
        }

    # Yahoo Finance already provides these fields in our format.
    if provider == "Yahoo Finance via yfinance":
        return {
            "ticker": raw_data.get("ticker", symbol),
            "company_name": raw_data.get("company_name"),
            "currency": raw_data.get("currency"),
            "financials": raw_data.get("financials", {}),
            "history": raw_data.get("history", {}),
            "data_source": provider,
            "error": None,
            "raw_data": raw_data,
        }

    # FMP provides separate statement records.
    profile = raw_data.get("company_profile", {})
    income = raw_data.get("income_statement", [])
    balance = raw_data.get("balance_sheet", [])
    cash_flow = raw_data.get("cash_flow_statement", [])

    latest_income = income[0] if isinstance(income, list) and income else {}
    latest_balance = balance[0] if isinstance(balance, list) and balance else {}
    latest_cash_flow = cash_flow[0] if isinstance(cash_flow, list) and cash_flow else {}

    financials = {
        "revenue": latest_income.get("revenue"),
        "net_income": latest_income.get("netIncome"),
        "operating_income": latest_income.get("operatingIncome"),
        "total_assets": latest_balance.get("totalAssets"),
        "shareholders_equity": latest_balance.get("totalStockholdersEquity"),
        "total_debt": latest_balance.get("totalDebt"),
        "operating_cash_flow": latest_cash_flow.get(
            "operatingCashFlow",
            latest_cash_flow.get("netCashProvidedByOperatingActivities"),
        ),
        "capital_expenditure": latest_cash_flow.get(
            "capitalExpenditure",
            latest_cash_flow.get("investmentsInPropertyPlantAndEquipment"),
        ),
    }

    history = {
        "revenue": [
            {"period": row.get("date"), "value": row.get("revenue")}
            for row in income
            if isinstance(row, dict) and row.get("revenue") is not None
        ] if isinstance(income, list) else [],
        "net_income": [
            {"period": row.get("date"), "value": row.get("netIncome")}
            for row in income
            if isinstance(row, dict) and row.get("netIncome") is not None
        ] if isinstance(income, list) else [],
        "operating_cash_flow": [
            {
                "period": row.get("date"),
                "value": row.get(
                    "operatingCashFlow",
                    row.get("netCashProvidedByOperatingActivities"),
                ),
            }
            for row in cash_flow
            if isinstance(row, dict)
            and row.get(
                "operatingCashFlow",
                row.get("netCashProvidedByOperatingActivities"),
            ) is not None
        ] if isinstance(cash_flow, list) else [],
    }

    return {
    "ticker": symbol,
    "company_name": profile.get("companyName"),
    "currency": profile.get("currency"),
    "current_price": profile.get("price"),
    "financials": financials,
    }


def get_stock_data(symbol):
    """Route a stock symbol and return a normalized data structure."""

    if not isinstance(symbol, str) or not symbol.strip():
        return {"error": "Please provide a valid stock symbol."}

    symbol = symbol.strip().upper()

    if symbol.endswith((".NS", ".BO")):
        provider = "Yahoo Finance via yfinance"
        raw_data = get_stock_snapshot(symbol)
    else:
        provider = "Financial Modeling Prep"
        raw_data = get_fmp_financials(symbol)

    return _normalize_stock_data(symbol, provider, raw_data)


if __name__ == "__main__":
    for symbol in ["AAPL", "RELIANCE.NS"]:
        result = get_stock_data(symbol)

        print(f"\n--- {symbol} ---")
        print("Provider:", result.get("data_source"))
        print("Company:", result.get("company_name"))
        print("Currency:", result.get("currency"))
        print("Financials:", result.get("financials"))
        print("Error:", result.get("error"))
