
from agents.financial_data_agent import FinancialDataAgent
from agents.live_price_agent import LivePriceAgent
from agents.verified_news_agent import VerifiedNewsAgent
from agents.investment_memo_schema import InvestmentMemo


class InvestmentOrchestrator:
    """Coordinate specialist agents and produce an investment memo."""

    def __init__(
        self,
        financial_agent=None,
        price_agent=None,
        news_agent=None,
    ):
        self.financial_agent = (
            financial_agent or FinancialDataAgent()
        )
        self.price_agent = price_agent or LivePriceAgent()
        self.news_agent = news_agent or VerifiedNewsAgent()

    def analyse(self, ticker_symbol):
        """Run specialist agents and return a structured investment memo."""

        if not isinstance(ticker_symbol, str) or not ticker_symbol.strip():
            return {"error": "Please provide a valid stock ticker."}

        ticker = ticker_symbol.strip().upper()

        financial_result = self.financial_agent.analyse(ticker)
        price_result = self.price_agent.analyse(ticker)
        news_result = self.news_agent.analyse(ticker)

        company_name = (
            financial_result.get("company_name")
            or price_result.get("company_name")
        )
        currency = (
            financial_result.get("currency")
            or price_result.get("currency")
        )

        key_strengths = financial_result.get("strengths", [])
        key_concerns = financial_result.get("concerns", [])
        risks_and_limitations = list(
            financial_result.get("data_limitations", [])
        )

        analysis_errors = []

        if financial_result.get("error"):
            analysis_errors.append(
                f"Financial analysis: {financial_result['error']}"
            )

        if price_result.get("error"):
            analysis_errors.append(
                f"Price analysis: {price_result['error']}"
            )

        if news_result.get("error"):
            analysis_errors.append(
                f"News analysis: {news_result['error']}"
            )

        risks_and_limitations.extend(analysis_errors)

        if analysis_errors:
            overall_summary = (
                "The investment assessment is incomplete because "
                "one or more specialist analyses reported an error."
            )
        else:
            overall_summary = financial_result.get(
                "summary",
                "Financial, price and news data were retrieved, but no "
                "investment recommendation has been assessed.",
            )

        memo = InvestmentMemo(
            ticker=ticker,
            company_name=company_name,
            currency=currency,
            financial_analysis=financial_result,
            price_analysis=price_result,
            news_analysis=news_result,
            key_strengths=key_strengths,
            key_concerns=key_concerns,
            risks_and_limitations=risks_and_limitations,
            overall_summary=overall_summary,
            recommendation="NOT_ASSESSED",
        )

        return memo.model_dump()
