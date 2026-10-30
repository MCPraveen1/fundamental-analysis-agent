import json

from agents.investment_orchestrator import InvestmentOrchestrator


def main():
    ticker = input("Enter a stock ticker (e.g., AAPL): ").strip()

    orchestrator = InvestmentOrchestrator()
    memo = orchestrator.analyse(ticker)

    print("\n" + "=" * 60)
    print("FUNDAMENTAL ANALYSIS INVESTMENT MEMO")
    print("=" * 60)
    print(json.dumps(memo, indent=2, default=str))

    if memo.get("error"):
        print("\nThe memo could not be generated.")
    else:
        print("\nOverall summary:")
        print(memo["overall_summary"])

        print("\nRecommendation:")
        print(memo["recommendation"])


if __name__ == "__main__":
    main()
