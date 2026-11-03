from fastapi import FastAPI, HTTPException
from api.schemas import AnalysisRequest
from agents.investment_orchestrator import InvestmentOrchestrator

app = FastAPI(
    title="Fundamental Analysis Agent API",
    description="AI-powered fundamental stock analysis API",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "Fundamental Analysis Agent API is running",
    }

@app.post("/analyse")
def analyse_stock(request: AnalysisRequest):
    orchestrator = InvestmentOrchestrator()
    result = orchestrator.analyse(request.ticker)

    if result.get("error"):
        raise HTTPException(
            status_code=400,
            detail=result["error"],
        )

    return result