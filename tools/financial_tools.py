
import math
import yfinance as yf


def _safe_number(value):
    """Convert a value to a finite float, or None if unavailable."""
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except (TypeError, ValueError):
        return None


def _format_period(period):
    """Convert a reporting period into a readable date string."""
    if hasattr(period, "strftime"):
        return period.strftime("%Y-%m-%d")
    return str(period)


def _latest_value(statement, row_name):
    """Return the latest available value for a financial statement row."""
    if statement is None or statement.empty:
        return None

    if row_name not in statement.index:
        return None

    values = statement.loc[row_name].dropna()

    if values.empty:
        return None

    return _safe_number(values.iloc[0])


def _statement_periods(statement):
    """Return available reporting periods, newest first."""
    if statement is None or statement.empty:
        return []

    return [_format_period(column) for column in statement.columns]


def _history(statement, row_name, limit=5):
    """Return historical values together with their reporting periods."""
    if statement is None or statement.empty:
        return []

    if row_name not in statement.index:
        return []

    values = statement.loc[row_name].dropna()
    history = []

    for period, value in values.items():
        number = _safe_number(value)

        if number is not None:
            history.append(
                {
                    "period": _format_period(period),
                    "value": number,
                }
            )

        if len(history) >= limit:
            break

    return history


def calculate_ratios(financials):
    """Calculate fundamental financial metrics from supplied values."""

    revenue = financials.get("revenue")
    net_income = financials.get("net_income")
    operating_income = financials.get("operating_income")
    assets = financials.get("total_assets")
    equity = financials.get("shareholders_equity")
    operating_cash_flow = financials.get("operating_cash_flow")
    capex = financials.get("capital_expenditure")

    return {
        "profit_margin": (
            net_income / revenue
            if net_income is not None and revenue not in (None, 0)
            else None
        ),
        "operating_margin": (
            operating_income / revenue
            if operating_income is not None
            and revenue not in (None, 0)
            else None
        ),
        "return_on_assets": (
            net_income / assets
            if net_income is not None and assets not in (None, 0)
            else None
        ),
        "return_on_equity": (
            net_income / equity
            if net_income is not None and equity not in (None, 0)
            else None
        ),
        "free_cash_flow": (
            operating_cash_flow + capex
            if operating_cash_flow is not None and capex is not None
            else None
        ),
    }


def get_stock_snapshot(ticker_symbol):
    """
    Retrieve company information, annual financial statements,
    historical values, and fundamental ratios.

    Examples:
        AAPL          - Apple, US market
        RELIANCE.NS   - Reliance Industries, NSE
        TCS.NS        - TCS, NSE
        500325.BO     - Reliance Industries, BSE
    """
    if not isinstance(ticker_symbol, str) or not ticker_symbol.strip():
        return {"error": "Please provide a valid stock ticker."}

    ticker_symbol = ticker_symbol.strip().upper()

    try:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info or {}

        income = stock.income_stmt
        balance = stock.balance_sheet
        cash_flow = stock.cashflow

        financials = {
    "revenue": _latest_value(income, "Total Revenue"),
    "net_income": _latest_value(income, "Net Income"),
    "operating_income": _latest_value(
        income, "Operating Income"
    ),
    "total_assets": _latest_value(balance, "Total Assets"),
    "shareholders_equity": _latest_value(
        balance, "Stockholders Equity"
    ),
    "total_debt": _latest_value(balance, "Total Debt"),
    "operating_cash_flow": _latest_value(
        cash_flow, "Operating Cash Flow"
    ),
    "capital_expenditure": _latest_value(
        cash_flow, "Capital Expenditure"
    ),
}

        return {
            "ticker": ticker_symbol,
            "company_name": info.get("longName"),
            "currency": info.get("currency"),
            "market_cap": _safe_number(info.get("marketCap")),
            "current_price": _safe_number(info.get("currentPrice")),
            "financials": financials,
            "reporting_periods": {
                "income_statement": _statement_periods(income),
                "balance_sheet": _statement_periods(balance),
                "cash_flow": _statement_periods(cash_flow),
            },
            "history": {
                "revenue": _history(income, "Total Revenue"),
                "net_income": _history(income, "Net Income"),
                "operating_cash_flow": _history(
                    cash_flow, "Operating Cash Flow"
                ),
            },
            "ratios": calculate_ratios(financials),
            "data_source": "Yahoo Finance via yfinance",
            "note": (
                "Annual statement values may not reflect the latest "
                "quarter. Verify reporting periods and source data."
            ),
        }

    except Exception as exc:
        return {
            "ticker": ticker_symbol,
            "error": str(exc),
            "data_source": "Yahoo Finance via yfinance",
        }


if __name__ == "__main__":
    result = get_stock_snapshot("AAPL")

    for section, values in result.items():
        print(f"\n{section.upper()}")
        print(values)
