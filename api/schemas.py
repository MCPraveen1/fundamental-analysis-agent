from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    ticker: str = Field(
        ...,
        min_length=1,
        description="Stock ticker symbol, e.g. AAPL or RELIANCE.NS",
    )