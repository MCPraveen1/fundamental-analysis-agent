
from pydantic import BaseModel, Field


class FinancialMetrics(BaseModel):
    profit_margin: float | None = None
    operating_margin: float | None = None
    return_on_assets: float | None = None
    return_on_equity: float | None = None
    free_cash_flow: float | None = None


class FinancialAnalysisReport(BaseModel):
    ticker: str
    company_name: str | None = None
    currency: str | None = None
    data_source: str

    metrics: FinancialMetrics

    strengths: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    data_limitations: list[str] = Field(default_factory=list)
    summary: str
    evaluation_issues: list[str] = Field(default_factory=list)
