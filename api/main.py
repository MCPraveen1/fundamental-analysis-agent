from io import BytesIO

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from api.schemas import AnalysisRequest
from agents.investment_orchestrator import InvestmentOrchestrator
from reports.pdf_generator import generate_investment_pdf

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


@app.post(
    "/analyse/pdf",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {
                "application/pdf": {
                    "schema": {
                        "type": "string",
                        "format": "binary"
                    }
                }
            },
            "description": "PDF investment report"
        }
    }
)
def analyse_stock_pdf(request: AnalysisRequest):
    orchestrator = InvestmentOrchestrator()
    result = orchestrator.analyse(request.ticker)

    if result.get("error"):
        raise HTTPException(
            status_code=400,
            detail=result["error"],
        )

    pdf_bytes = generate_investment_pdf(result)

    filename = (
        f"{result.get('ticker', request.ticker)}_investment_report.pdf"
    )

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )
