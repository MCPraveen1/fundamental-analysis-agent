
from agents.financial_data_agent import FinancialDataAgent
from agents.live_price_agent import LivePriceAgent


class InvestmentOrchestrator:
    """Coordinate specialist agents and combine their results."""

    def __init__(self, financial_agent=None, price_agent=None):
        self.financial_agent = (
            financial_agent or FinancialDataAgent()
        )
        self.price_agent = price_agent or LivePriceAgent()

    def analyse(self, ticker_symbol):
        """Run both agents and return a combined structured result."""

        if not isinstance(ticker_symbol, str) or not ticker_symbol.strip():
            return {"error": "Please provide a valid stock ticker."}

        ticker = ticker_symbol.strip().upper()

        financial_result = self.financial_agent.analyse(ticker)
        price_result = self.price_agent.analyse(ticker)

        # Preserve each agent's result, including individual errors.
        return {
            "ticker": ticker,
            "financial_analysis": financial_result,
            "price_analysis": price_result,
        }
