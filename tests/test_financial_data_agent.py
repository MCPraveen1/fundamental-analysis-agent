
import json

from agents.financial_data_agent import FinancialDataAgent


def test_agent_sends_calculated_metrics_to_llm(monkeypatch):
    """Verify calculated metrics reach the LLM and its report is parsed."""

    financial_snapshot = {
        "ticker": "AAPL",
        "company_name": "Apple Inc.",
        "currency": "USD",
        "data_source": "Test provider",
        "financials": {
            "revenue": 1000,
            "net_income": 100,
            "operating_income": 150,
            "total_assets": 500,
            "shareholders_equity": 250,
            "operating_cash_flow": 180,
            "capital_expenditure": -40,
        },
        "history": {},
        "error": None,
    }

    monkeypatch.setattr(
        "agents.financial_data_agent.get_stock_data",
        lambda ticker: financial_snapshot,
    )

    captured = {}

    class FakeCompletions:
        def create(self, **kwargs):
            captured["messages"] = kwargs["messages"]

            fake_json = json.dumps({
                "strengths": ["Positive cash flow"],
                "concerns": [],
                "data_limitations": [],
                "summary": "Test analysis",
            })

            return type(
                "Response",
                (),
                {
                    "choices": [
                        type(
                            "Choice",
                            (),
                            {
                                "message": type(
                                    "Message",
                                    (),
                                    {"content": fake_json},
                                )()
                            },
                        )()
                    ]
                },
            )()

    agent = FinancialDataAgent.__new__(FinancialDataAgent)
    agent.model = "test-model"
    agent.client = type(
        "Client",
        (),
        {
            "chat": type(
                "Chat",
                (),
                {"completions": FakeCompletions()},
            )()
        },
    )()

    result = agent.analyse("AAPL")

    user_message = next(
        message["content"]
        for message in captured["messages"]
        if message["role"] == "user"
    )

    json_text = user_message.split(
        "Financial snapshot:\n", 1
    )[1].split("\n\nExplain:", 1)[0]
    payload = json.loads(json_text)

    assert result["summary"] == "Test analysis"
    assert result["metrics"]["free_cash_flow"] == 140
    assert result["metrics"]["profit_margin"] == 0.10
    assert payload["calculated_metrics"]["free_cash_flow"] == 140

    
def test_agent_flags_unsupported_industry_comparison(monkeypatch):
    """Verify evaluator findings appear in the returned report."""

    financial_snapshot = {
        "ticker": "AAPL",
        "company_name": "Apple Inc.",
        "currency": "USD",
        "data_source": "Test provider",
        "financials": {
            "revenue": 1000,
            "net_income": 100,
            "operating_income": 150,
            "total_assets": 500,
            "shareholders_equity": 250,
            "operating_cash_flow": 180,
            "capital_expenditure": -40,
        },
        "history": {},
        "error": None,
    }

    monkeypatch.setattr(
        "agents.financial_data_agent.get_stock_data",
        lambda ticker: financial_snapshot,
    )

    class FakeCompletions:
        def create(self, **kwargs):
            fake_json = json.dumps({
                "strengths": [
                    "The company outperforms the industry"
                ],
                "concerns": [],
                "data_limitations": [],
                "summary": "Test analysis",
            })

            return type(
                "Response",
                (),
                {
                    "choices": [
                        type(
                            "Choice",
                            (),
                            {
                                "message": type(
                                    "Message",
                                    (),
                                    {"content": fake_json},
                                )()
                            },
                        )()
                    ]
                },
            )()

    agent = FinancialDataAgent.__new__(FinancialDataAgent)
    agent.model = "test-model"
    agent.client = type(
        "Client",
        (),
        {
            "chat": type(
                "Chat",
                (),
                {"completions": FakeCompletions()},
            )()
        },
    )()

    result = agent.analyse("AAPL")

    assert "Unsupported industry comparison" in result[
        "evaluation_issues"
    ]

