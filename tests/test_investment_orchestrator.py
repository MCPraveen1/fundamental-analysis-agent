
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


class FakeNewsAgent:
    def analyse(self, ticker):
        return {
            "ticker": ticker,
            "provider": "Test provider",
            "articles": [
                {
                    "headline": "Example company news",
                    "url": "https://example.com/news",
                    "evidence_status": "metadata_complete",
                    "claims_independently_verified": False,
                }
            ],
        }


def test_orchestrator_combines_agent_results():
    orchestrator = InvestmentOrchestrator(
        financial_agent=FakeFinancialAgent(),
        price_agent=FakePriceAgent(),
        news_agent=FakeNewsAgent(),
    )

    result = orchestrator.analyse("aapl")

    assert result["ticker"] == "AAPL"
    assert (
        result["financial_analysis"]["summary"]
        == "Financial analysis completed"
    )
    assert result["price_analysis"]["current_price"] == 225.50
    assert result["news_analysis"]["provider"] == "Test provider"
    assert result["news_analysis"]["articles"][0]["headline"] == (
        "Example company news"
    )
    assert result["recommendation"] == "NOT_ASSESSED"


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
        news_agent=FakeNewsAgent(),
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
    assert (
        "Price analysis: Current price is unavailable."
        in result["risks_and_limitations"]
    )
    assert result["recommendation"] == "NOT_ASSESSED"


def test_orchestrator_rejects_empty_ticker():
    orchestrator = InvestmentOrchestrator(
        financial_agent=FakeFinancialAgent(),
        price_agent=FakePriceAgent(),
        news_agent=FakeNewsAgent(),
    )

    result = orchestrator.analyse("  ")

    assert result["error"] == "Please provide a valid stock ticker."


def test_orchestrator_preserves_news_error():
    class FailingNewsAgent:
        def analyse(self, ticker):
            return {
                "ticker": ticker,
                "error": "The news search request failed.",
                "articles": [],
            }

    orchestrator = InvestmentOrchestrator(
        financial_agent=FakeFinancialAgent(),
        price_agent=FakePriceAgent(),
        news_agent=FailingNewsAgent(),
    )

    result = orchestrator.analyse("AAPL")

    assert (
        result["financial_analysis"]["summary"]
        == "Financial analysis completed"
    )
    assert result["price_analysis"]["current_price"] == 225.50
    assert (
        result["news_analysis"]["error"]
        == "The news search request failed."
    )
    assert (
        "News analysis: The news search request failed."
        in result["risks_and_limitations"]
    )
    assert result["recommendation"] == "NOT_ASSESSED"

def test_orchestrator_preserves_news_quality_metadata():
    class NewsAgentWithQualityMetadata:
        def analyse(self, ticker):
            return {
                "ticker": ticker,
                "provider": "Test provider",
                "articles": [
                    {
                        "headline": "Example company news",
                        "url": "https://example.com/news",
                        "evidence_status": "metadata_complete",
                        "freshness_status": "fresh",
                        "duplicate": True,
                        "duplicate_reasons": ["Duplicate URL"],
                        "claims_independently_verified": False,
                    }
                ],
            }

    orchestrator = InvestmentOrchestrator(
        financial_agent=FakeFinancialAgent(),
        price_agent=FakePriceAgent(),
        news_agent=NewsAgentWithQualityMetadata(),
    )

    result = orchestrator.analyse("AAPL")
    article = result["news_analysis"]["articles"][0]

    assert article["freshness_status"] == "fresh"
    assert article["duplicate"] is True
    assert article["duplicate_reasons"] == ["Duplicate URL"]
