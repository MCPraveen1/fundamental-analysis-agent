
from agents.investment_orchestrator import InvestmentOrchestrator
from reports.pdf_generator import generate_investment_pdf


def main():
    ticker = "AAPL"

    print(f"Running investment analysis for {ticker}...")

    orchestrator = InvestmentOrchestrator()
    memo = orchestrator.analyse(ticker)

    if memo.get("error"):
        print(f"Analysis failed: {memo['error']}")
        return

    print("Analysis completed.")
    print("Generating PDF...")

    output_path = f"reports/{ticker}_investment_report.pdf"

    generate_investment_pdf(
        memo,
        output_path=output_path,
    )

    print(f"PDF generated: {output_path}")


if __name__ == "__main__":
    main()
