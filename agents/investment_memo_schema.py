
from enum import Enum
from pydantic import BaseModel, Field


class Recommendation(str, Enum):
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    NOT_ASSESSED = "NOT_ASSESSED"

class InvestmentMemo(BaseModel):
    """Structured investment memo built from specialist-agent results."""

    ticker: str
    company_name: str | None = None
    currency: str | None = None

    financial_analysis: dict
    price_analysis: dict
    news_analysis: dict = Field(default_factory=dict)

    key_strengths: list[str] = Field(default_factory=list)
    key_concerns: list[str] = Field(default_factory=list)
    risks_and_limitations: list[str] = Field(default_factory=list)

    overall_summary: str
    recommendation: Recommendation = Recommendation.NOT_ASSESSED
