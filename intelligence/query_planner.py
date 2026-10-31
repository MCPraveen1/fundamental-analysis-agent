DEFAULT_PERIOD_DAYS = 7

QUERY_TEMPLATES = {
    "company_developments": (
        "{company_name} latest company announcements investments acquisitions"
    ),
    "financial_performance": (
        "{company_name} earnings revenue margins financial results"
    ),
    "market_reaction": (
        "{company_name} {exchange} share price trading volume market reaction"
    ),
    "expert_analysis": (
        "{company_name} analyst opinions valuation forecasts outlook"
    ),
}


def build_search_queries(identity, period_days=DEFAULT_PERIOD_DAYS):
    """Generate focused financial news queries for a company."""

    if not isinstance(identity, dict):
        raise ValueError("Company identity must be a dictionary.")

    ticker = identity.get("ticker")
    company_name = identity.get("company_name")
    market = identity.get("market")
    exchange = identity.get("exchange")

    if not all(
        isinstance(value, str) and value.strip()
        for value in (ticker, company_name, market, exchange)
    ):
        raise ValueError("Company identity is incomplete.")

    if not isinstance(period_days, int) or isinstance(period_days, bool):
        raise ValueError("period_days must be an integer.")

    if period_days < 1:
        raise ValueError("period_days must be at least 1.")

    company_name = company_name.strip()
    market = market.strip().upper()
    exchange = exchange.strip().upper()

    if market not in {"INDIA", "US"}:
        raise ValueError(f"Unsupported market: {market}")

    if market == "INDIA":
        exchange_term = f"{exchange} India"
    else:
        exchange_term = "US stock market"

    queries = []

    for category, template in QUERY_TEMPLATES.items():
        query = template.format(
            company_name=company_name,
            exchange=exchange_term,
        )

        queries.append(
            {
                "category": category,
                "query": query,
            }
        )

    return {
        "ticker": ticker.strip().upper(),
        "company_name": company_name,
        "market": market,
        "period_days": period_days,
        "queries": queries,
    }