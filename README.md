# Fundamental Analysis Agent 📊

A Python-based AI project that retrieves financial data for US and Indian stocks, standardizes the data across providers, and uses a Large Language Model (LLM) to generate fundamental financial analysis.

## 🎯 Project Overview

The goal of this project is to build a multi-agent AI system for stock fundamental analysis. It combines financial data retrieval, deterministic financial calculations, and LLM-powered interpretation to make company financial information easier to understand.

The project is being developed incrementally, with an emphasis on reliable data, modular tools, and responsible AI-generated analysis.

## ✨ Current Features

- **Multi-source financial data:** Uses Financial Modeling Prep (FMP) for supported US stocks and Yahoo Finance through `yfinance` for Indian stocks.
- **Normalized data structure:** Routes stock symbols to the appropriate provider and standardizes the resulting financial data.
- **Financial statement retrieval:** Retrieves available income statement, balance sheet, and cash flow information.
- **Historical financial data:** Provides selected financial metrics across reporting periods.
- **LLM-powered analysis:** Uses Groq to generate a narrative analysis based on retrieved financial information.
- **Error handling:** Handles invalid symbols and provider access restrictions.
- **Unit testing:** Includes tests for core financial tools.

## 🛠️ Technology Stack

- Python 3.12
- Groq API
- Financial Modeling Prep API
- Yahoo Finance (`yfinance`)
- Pandas and NumPy
- Requests
- python-dotenv
- Pytest

## 🏗️ Project Structure

```text
fundamental-analysis-agent/
├── agents/
│   ├── __init__.py
│   └── financial_data_agent.py
├── reports/
├── tests/
│   └── test_financial_tools.py
├── tools/
│   ├── __init__.py
│   ├── financial_tools.py
│   ├── fmp_tools.py
│   └── stock_data_router.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## ⚙️ Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/MCPraveen1/fundamental-analysis-agent.git
cd fundamental-analysis-agent
```

### 2. Create a virtual environment

```bash
py -3.12 -m venv .venv
```

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root using `.env.example` as a template.

Add your own API credentials:

```text
GROQ_API_KEY=your_groq_api_key
FMP_API_KEY=your_fmp_api_key
```

**Security:** Never commit `.env` or publish API keys to GitHub.

## ▶️ Running the Project

Run the financial data agent:

```bash
python -m agents.financial_data_agent
```

Test the financial data router:

```bash
python -m tools.stock_data_router
```

Run the unit tests:

```bash
python -m pytest tests/test_financial_tools.py -v
```

## 🧪 Example Stock Symbols

| Market | Example symbol | Data provider |
|---|---|---|
| US | `AAPL` | Financial Modeling Prep |
| India | `RELIANCE.NS` | Yahoo Finance via `yfinance` |

Provider availability depends on API access, subscription limits, and data availability.

## 🗺️ Development Roadmap

- [x] Retrieve financial data from multiple providers
- [x] Normalize financial data into a common structure
- [x] Build an initial LLM-powered financial analysis agent
- [x] Add initial unit tests for financial tools
- [ ] Calculate and validate key financial ratios deterministically in Python
- [ ] Add specialist agents for deeper financial analysis
- [ ] Build an orchestrator to coordinate agents
- [ ] Improve report generation and evaluation
- [ ] Add more comprehensive tests and documentation

## ⚠️ Disclaimer

This project is for educational and research purposes only. It does not provide personalized financial advice or recommendations to buy, hold, or sell securities. Financial data may be incomplete, delayed, or subject to provider limitations. Always verify information independently before making investment decisions.

## 👨‍💻 Author

**Praveen MC**

- GitHub: [MCPraveen1](https://github.com/MCPraveen1)
- Portfolio: [View my portfolio](https://mcpraveen1.github.io/Portfolio/)