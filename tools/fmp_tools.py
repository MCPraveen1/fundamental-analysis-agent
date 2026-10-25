
import os

import requests
from dotenv import load_dotenv

load_dotenv()

FMP_BASE_URL = "https://financialmodelingprep.com/stable"


def _fmp_get(endpoint, symbol, limit=5):
    """Make a request to an FMP endpoint."""

    api_key = os.getenv("FMP_API_KEY")

    if not api_key:
        return {"error": "FMP_API_KEY is missing from .env"}

    if not isinstance(symbol, str) or not symbol.strip():
        return {"error": "Please provide a valid stock symbol."}

    url = f"{FMP_BASE_URL}/{endpoint}"

    try:
        response = requests.get(
            url,
            params={
                "symbol": symbol.strip().upper(),
                "limit": limit,
                "apikey": api_key,
            },
            timeout=20,
        )

        response.raise_for_status()
        data = response.json()

        if isinstance(data, dict) and data.get("error"):
            return {"error": str(data["error"])}

        if not isinstance(data, list) or not data:
            return {
                "symbol": symbol.strip().upper(),
                "error": (
                    f"No data returned by FMP endpoint: {endpoint}. "
                    "Check the symbol and endpoint access."
                ),
            }

        return data

    
    except requests.HTTPError as exc:
        status_code = (
            exc.response.status_code
            if exc.response is not None
            else None
        )

        if status_code == 402:
            return {
                "error": (
                    "FMP access restricted (HTTP 402: Payment Required). "
                    "The current plan may not include this endpoint or market."
                ),
                "status_code": 402,
                "data_source": "Financial Modeling Prep",
            }

        if status_code == 403:
            return {
                "error": (
                    "FMP access forbidden (HTTP 403). "
                    "Check endpoint permissions and subscription access."
                ),
                "status_code": 403,
                "data_source": "Financial Modeling Prep",
            }

        return {
            "error": f"FMP HTTP request failed: {exc}",
            "status_code": status_code,
            "data_source": "Financial Modeling Prep",
        }

    except requests.RequestException as exc:
        return {
            "error": f"FMP network request failed: {exc}",
            "data_source": "Financial Modeling Prep",
        }


    except ValueError:
        return {"error": "FMP returned an invalid JSON response."}


def get_company_profile(symbol):
    """Retrieve the company's profile."""
    result = _fmp_get("profile", symbol, limit=1)

    if isinstance(result, list):
        return result[0]

    return result


def get_income_statement(symbol, limit=5):
    """Retrieve annual income statement records."""
    return _fmp_get("income-statement", symbol, limit)


def get_balance_sheet(symbol, limit=5):
    """Retrieve annual balance sheet records."""
    return _fmp_get("balance-sheet-statement", symbol, limit)


def get_cash_flow_statement(symbol, limit=5):
    """Retrieve annual cash flow statement records."""
    return _fmp_get("cash-flow-statement", symbol, limit)


def get_fmp_financials(symbol, limit=5):
    """Collect the profile and three financial statement datasets."""

    profile = get_company_profile(symbol)

    if profile.get("error"):
        return {
            "symbol": symbol.strip().upper(),
            "error": profile["error"],
        }

    return {
        "symbol": symbol.strip().upper(),
        "company_profile": profile,
        "income_statement": get_income_statement(symbol, limit),
        "balance_sheet": get_balance_sheet(symbol, limit),
        "cash_flow_statement": get_cash_flow_statement(symbol, limit),
        "data_source": "Financial Modeling Prep",
    }


if __name__ == "__main__":
    result = get_fmp_financials("AAPL", limit=5)

    for section, data in result.items():
        print(f"\n{section.upper()}")
        print(data)
