
from agents.investment_orchestrator import InvestmentOrchestrator


class FakeFinancialAgent:
    def analyse(self, ticker):
        return {
            "ticker": ticker,
            "summary": "Financial analysis completed",
        }


class FakePriceAgent:
    def analyse(self, ticker):
        return {
            "ticker": ticker,
            "current_price": 225.50,
            "currency": "USD",
        }


def test_orchestrator_combines_both_agent_results():
    orchestrator = InvestmentOrchestrator(
        financial_agent=FakeFinancialAgent(),
        price_agent=FakePriceAgent(),
    )

    result = orchestrator.analyse("aapl")

    assert result["ticker"] == "AAPL"
    assert (
        result["financial_analysis"]["summary"]
        == "Financial analysis completed"
    )
    assert result["price_analysis"]["current_price"] == 225.50


def test_orchestrator_preserves_price_error():
    class FailingPriceAgent:
        def analyse(self, ticker):
            return {
                "ticker": ticker,
                "error": "Current price is unavailable.",
            }

    orchestrator = InvestmentOrchestrator(
        financial_agent=FakeFinancialAgent(),
        price_agent=FailingPriceAgent(),
    )

    result = orchestrator.analyse("AAPL")

    assert (
        result["financial_analysis"]["summary"]
        == "Financial analysis completed"
    )
    assert (
        result["price_analysis"]["error"]
        == "Current price is unavailable."
    )


def test_orchestrator_rejects_empty_ticker():
    orchestrator = InvestmentOrchestrator(
        financial_agent=FakeFinancialAgent(),
        price_agent=FakePriceAgent(),
    )

    result = orchestrator.analyse("  ")

    assert result["error"] == "Please provide a valid stock ticker."
