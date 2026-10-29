
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

    @staticmethod
    def _run_agent(agent, ticker, label):
        """Run an agent and convert unexpected exceptions into errors."""
        try:
            return agent.analyse(ticker)
        except Exception as exc:
            return {
                "ticker": ticker,
                "error": f"{label} failed: {exc}",
            }

    def analyse(self, ticker_symbol):
        """Run specialist agents and return a structured investment memo."""

        if not isinstance(ticker_symbol, str) or not ticker_symbol.strip():
            return {"error": "Please provide a valid stock ticker."}

        ticker = ticker_symbol.strip().upper()

        financial_result = self._run_agent(
            self.financial_agent, ticker, "Financial analysis"
        )
        price_result = self._run_agent(
            self.price_agent, ticker, "Price analysis"
        )
        news_result = self._run_agent(
            self.news_agent, ticker, "News analysis"
        )
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
        for article in news_result.get("articles", []):
            if not isinstance(article, dict):
                continue

            if article.get("duplicate"):
                reasons = article.get("duplicate_reasons", [])
                reason_text = ", ".join(reasons) if reasons else (
                    "duplicate article detected"
                )
                risks_and_limitations.append(
                    f"News quality risk: {reason_text}"
                )

            if article.get("freshness_status") == "stale":
                risks_and_limitations.append(
                    "News quality risk: Article is stale."
                )

        summary_parts = []

        financial_summary = financial_result.get("summary")
        if financial_summary:
            summary_parts.append(
                f"Financial analysis: {financial_summary}"
            )

        price_summary = price_result.get("summary")
        if price_summary:
            summary_parts.append(
                f"Price analysis: {price_summary}"
            )

        headlines = [
            article.get("headline")
            for article in news_result.get("articles", [])
            if isinstance(article, dict)
            and isinstance(article.get("headline"), str)
            and article["headline"].strip()
        ]

        if headlines:
            summary_parts.append(
                "News highlights: " + "; ".join(headlines[:3])
            )

        if analysis_errors:
            summary_parts.append(
                "The investment assessment is incomplete because "
                "one or more specialist analyses reported an error."
            )

        overall_summary = " ".join(summary_parts) or (
            "Analysis results are limited. No investment recommendation "
            "has been assessed."
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
