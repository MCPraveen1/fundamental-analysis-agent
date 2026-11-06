
from io import BytesIO
from datetime import datetime
from enum import Enum
from xml.sax.saxutils import escape

from email.utils import parsedate_to_datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def _to_dict(data):
    """Convert Pydantic models or dictionaries into dictionaries."""
    if hasattr(data, "model_dump"):
        return data.model_dump(mode="json")

    return data if isinstance(data, dict) else {}


def _safe_text(value):
    """Escape and normalize text for ReportLab Paragraph rendering."""
    if value is None:
        return "N/A"

    if isinstance(value, Enum):
        value = value.value

    text = str(value)

    # Normalize Unicode hyphens for Helvetica compatibility.
    text = text.replace("\u2011", "-")

    return escape(text)


def _format_value(value):
    """Format nested values without losing their information."""
    if value is None:
        return "N/A"

    if isinstance(value, dict):
        return "; ".join(
            f"{key}: {_format_value(val)}"
            for key, val in value.items()
        )

    if isinstance(value, list):
        return "; ".join(_format_value(item) for item in value)

    if isinstance(value, bool):
        return "Yes" if value else "No"

    return _safe_text(value)


def _add_page_number(canvas, doc):
    """Add a footer and page number."""
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)

    canvas.drawString(
        20 * mm,
        12 * mm,
        "Fundamental Analysis Agent | Research Report",
    )

    canvas.drawRightString(
        190 * mm,
        12 * mm,
        f"Page {doc.page}",
    )

    canvas.restoreState()


def _add_heading(story, title, styles):
    story.append(
        Paragraph(title, styles["SectionHeading"])
    )


def _add_paragraph(story, text, styles):
    story.append(
        Paragraph(_safe_text(text), styles["ReportBody"])
    )


def _add_bullet_section(story, title, items, styles):
    """Display strengths, concerns and limitations."""
    _add_heading(story, title, styles)

    if not items:
        _add_paragraph(story, "No information available.", styles)
        return

    for item in items:
        story.append(
            Paragraph(
                f"&bull; {_safe_text(item)}",
                styles["ReportBody"],
            )
        )


def _add_table(story, headers, rows, styles, col_widths=None):
    """Create a consistently formatted table."""
    table_data = [
        [
            Paragraph(_safe_text(header), styles["TableHeader"])
            for header in headers
        ]
    ]

    for row in rows:
        table_data.append([
            Paragraph(_format_value(value), styles["TableCell"])
            for value in row
        ])

    table = Table(
        table_data,
        colWidths=col_widths,
        repeatRows=1,
        hAlign="LEFT",
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
                colors.white,
                colors.HexColor("#F2F5F9"),
            ]),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ])
    )

    story.append(table)
    story.append(Spacer(1, 8))


# --------------------------------------------------
# Financial analysis
# --------------------------------------------------

def _add_financial_analysis(story, financial, currency, styles):
    _add_heading(story, "Financial Performance", styles)

    metrics = financial.get("metrics", {})

    if hasattr(metrics, "model_dump"):
        metrics = metrics.model_dump()

    metrics = _to_dict(metrics)

    metric_labels = {
        "profit_margin": "Profit Margin (%)",
        "operating_margin": "Operating Margin (%)",
        "return_on_assets": "Return on Assets (%)",
        "return_on_equity": "Return on Equity (%)",
        "free_cash_flow": "Free Cash Flow",
    }

    rows = []

    
    for key, label in metric_labels.items():
        value = metrics.get(key)

        if value is None:
            display_value = "N/A"

        elif key == "free_cash_flow":
            if abs(value) >= 1_000_000_000:
                display_value = (
                    f"{currency} {value / 1_000_000_000:,.1f} billion"
                )
            elif abs(value) >= 1_000_000:
                display_value = (
                    f"{currency} {value / 1_000_000:,.1f} million"
                )
            else:
                display_value = f"{currency} {value:,.2f}"

        else:
            display_value = f"{value * 100:.1f}%"

        rows.append([label, display_value])


    _add_table(
        story,
        ["Financial Metric", "Value"],
        rows,
        styles,
        [75 * mm, 95 * mm],
    )

    _add_paragraph(
        story,
        f"Data source: {financial.get('data_source', 'N/A')}",
        styles,
    )

    _add_bullet_section(
        story,
        "Financial Strengths",
        financial.get("strengths", []),
        styles,
    )

    _add_bullet_section(
        story,
        "Financial Concerns",
        financial.get("concerns", []),
        styles,
    )

    _add_bullet_section(
        story,
        "Financial Data Limitations",
        financial.get("data_limitations", []),
        styles,
    )

    _add_bullet_section(
        story,
        "Report Evaluation Issues",
        financial.get("evaluation_issues", []),
        styles,
    )


# --------------------------------------------------
# Price analysis
# --------------------------------------------------

def _add_price_analysis(story, price, styles):
    _add_heading(story, "Latest Available Price", styles)

    current_price = price.get("current_price")
    currency = price.get("currency") or ""

    if current_price is None:
        display_price = "Not available"
    else:
        display_price = f"{currency} {current_price:,.2f}".strip()

    rows = [
        ["Latest available price", display_price],
        ["Data source", price.get("data_source", "N/A")],
    ]

    _add_table(
        story,
        ["Field", "Value"],
        rows,
        styles,
        [75 * mm, 95 * mm],
    )

    _add_paragraph(
        story,
        "This is the latest price returned by the configured data "
        "provider. It is not necessarily a real-time exchange quote.",
        styles,
    )


# --------------------------------------------------
# News analysis
# --------------------------------------------------

def _add_news_analysis(story, news, styles):
    _add_heading(story, "News Analysis", styles)

    if news.get("error"):
        _add_paragraph(
            story,
            f"News retrieval error: {news['error']}",
            styles,
        )
        return

    articles = news.get("articles", [])

    rows = []

    for article in articles:
        if not isinstance(article, dict):
            continue

        published_at = article.get("published_at", "Unknown")

        try:
            if isinstance(published_at, str):
                published_at = parsedate_to_datetime(
                    published_at
                ).strftime("%d %b %Y")
        except (ValueError, TypeError, OverflowError):
            pass

        rows.append([
            article.get("headline", "Headline unavailable"),
            article.get("source", "Unknown"),
            published_at,
            (
                "Complete"
                if article.get("evidence_status") == "metadata_complete"
                else "Incomplete"
            ),
            article.get("freshness_status", "Unknown"),
        ])

    if rows:
        _add_table(
            story,
            [
                "Headline",
                "Publisher",
                "Publication Date",
                "Metadata",
                "Freshness",
            ],
            rows,
            styles,
            [75 * mm, 25 * mm, 25 * mm, 25 * mm, 20 * mm],
        )

        # Add article links separately for readability.
        _add_heading(story, "Article Sources", styles)

        for index, article in enumerate(articles, start=1):
            if not isinstance(article, dict):
                continue

            headline = _safe_text(
                article.get("headline", "Untitled article")
            )

            url = article.get("url", "")
            source = _safe_text(article.get("source", "Unknown"))

            if (
                isinstance(url, str)
                and url.startswith(("http://", "https://"))
            ):
                link = (
                    f'<link href="{escape(url, {chr(34): "&quot;"})}" '
                    f'color="blue">Open article</link>'
                )
            else:
                link = "Link unavailable"

            story.append(
                Paragraph(
                    f"{index}. <b>{headline}</b> — {source} | {link}",
                    styles["ReportBody"],
                )
            )

            issues = article.get("evidence_issues", [])

            if issues:
                story.append(
                    Paragraph(
                        f"Metadata issues: {_format_value(issues)}",
                        styles["SmallText"],
                    )
                )

    else:
        _add_paragraph(
            story,
            "No news articles were retrieved.",
            styles,
        )

    _add_paragraph(
        story,
        news.get("verification_note", ""),
        styles,
    )


# --------------------------------------------------
# Financial intelligence
# --------------------------------------------------

def _add_financial_intelligence(story, intelligence, styles):
    _add_heading(
        story,
        "Financial Intelligence Assessment",
        styles,
    )

    if not intelligence:
        _add_paragraph(
            story,
            "Financial intelligence report unavailable.",
            styles,
        )
        return

    # Retrieval summary
    retrieval = intelligence.get("retrieval_summary", {})

    _add_heading(story, "Retrieval Summary", styles)

    if retrieval:
        rows = [
            [key.replace("_", " ").title(), value]
            for key, value in retrieval.items()
        ]

        _add_table(
            story,
            ["Measure", "Result"],
            rows,
            styles,
            [90 * mm, 80 * mm],
        )

    # Evidence classification
    evidence = intelligence.get("evidence_summary", {})
    evidence_counts = evidence.get("evidence_type_counts", {})

    _add_heading(story, "Evidence Classification", styles)

    if evidence_counts:
        rows = [
            [key.replace("_", " ").title(), value]
            for key, value in evidence_counts.items()
        ]

        _add_table(
            story,
            ["Evidence Type", "Article Count"],
            rows,
            styles,
            [110 * mm, 60 * mm],
        )

    # Source quality
    source_quality = intelligence.get("source_quality", {})

    _add_heading(story, "Source Quality", styles)

    if source_quality:
        rows = [
            [key.replace("_", " ").title(), value]
            for key, value in source_quality.items()
        ]

        _add_table(
            story,
            ["Source Measure", "Count"],
            rows,
            styles,
            [110 * mm, 60 * mm],
        )

    _add_paragraph(
        story,
        "Claims independently verified: "
        + _format_value(
            evidence.get("claims_independently_verified", False)
        ),
        styles,
    )

        # Category summary
    categories = intelligence.get("news_categories", {})

    category_labels = {
        "company_developments": "Company Developments",
        "financial_performance": "Financial Performance",
        "market_reaction": "Market Reaction",
        "expert_analysis": "Expert Analysis",
    }

    category_rows = []

    for category, label in category_labels.items():
        articles = categories.get(category, [])

        if articles:
            category_rows.append([
                label,
                len(articles),
            ])

    if category_rows:
        _add_heading(
            story,
            "News Category Distribution",
            styles,
        )

        _add_table(
            story,
            ["Category", "Article Count"],
            category_rows,
            styles,
            [110 * mm, 60 * mm],
        )

    # Limitations
    _add_bullet_section(
        story,
        "Intelligence Report Limitations",
        intelligence.get("limitations", []),
        styles,
    )

    # Rejected articles and search errors
    rejected = intelligence.get("rejected_articles", [])
    search_errors = intelligence.get("search_errors", [])

    _add_paragraph(
        story,
        f"Rejected articles: {len(rejected)}",
        styles,
    )

    if search_errors:
        _add_bullet_section(
            story,
            "Search Errors",
            search_errors,
            styles,
        )

    _add_paragraph(
        story,
        intelligence.get("verification_note", ""),
        styles,
    )


# --------------------------------------------------
# Main PDF generator
# --------------------------------------------------

def generate_investment_pdf(memo, output_path=None):
    """
    Generate a structured investment analysis PDF.

    Args:
        memo: InvestmentMemo instance or dictionary.
        output_path: Optional destination file path.

    Returns:
        PDF bytes if output_path is omitted.
        Otherwise, returns the output path.
    """

    data = _to_dict(memo)

    buffer = BytesIO()
    destination = output_path if output_path else buffer

    document = SimpleDocTemplate(
        destination,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=22 * mm,
        title="Investment Analysis Report",
        author="Fundamental Analysis Agent",
    )

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontSize=22,
            leading=28,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#17365D"),
            spaceAfter=12,
        )
    )

    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading2"],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#17365D"),
            spaceBefore=14,
            spaceAfter=8,
            keepWithNext=True,
        )
    )

    styles.add(
        ParagraphStyle(
            name="ReportBody",
            parent=styles["BodyText"],
            fontSize=9,
            leading=13,
            spaceAfter=6,
    )
    )

    styles.add(
        ParagraphStyle(
            name="TableCell",
            parent=styles["BodyText"],
            fontSize=7.5,
            leading=10,
        )
    )

    styles.add(
        ParagraphStyle(
            name="TableHeader",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=colors.white,
        )
    )

    styles.add(
        ParagraphStyle(
            name="SmallText",
            parent=styles["BodyText"],
            fontSize=7.5,
            leading=10,
            textColor=colors.grey,
        )
    )

    story = []

    ticker = data.get("ticker", "Unknown")
    company = data.get("company_name") or ticker
    currency = data.get("currency") or ""

    financial = _to_dict(data.get("financial_analysis", {}))
    price = _to_dict(data.get("price_analysis", {}))
    news = _to_dict(data.get("news_analysis", {}))
    intelligence = _to_dict(
        data.get("financial_intelligence_report", {})
    )

    # 1. Company overview
    story.append(
        Paragraph(
            "Investment Analysis Report",
            styles["ReportTitle"],
        )
    )

    story.append(
        Paragraph(
            _safe_text(company),
            styles["Heading2"],
        )
    )

    story.append(
        Paragraph(
            f"<b>Ticker:</b> {_safe_text(ticker)}",
            styles["ReportBody"],
        )
    )

    story.append(
        Paragraph(
            f"<b>Currency:</b> {_safe_text(currency or 'N/A')}",
            styles["ReportBody"],
        )
    )

    story.append(
        Paragraph(
            f"<b>Generated:</b> "
            f"{datetime.now().strftime('%d %B %Y, %H:%M')}",
            styles["ReportBody"],
        )
    )

    story.append(Spacer(1, 12))

    # 2. Executive summary
    _add_heading(story, "Executive Summary", styles)

    _add_paragraph(
        story,
        data.get("overall_summary", "No summary available."),
        styles,
    )

    # 3. Financial performance
    _add_financial_analysis(
        story,
        financial,
        currency,
        styles,
    )

    # 4. Price analysis
    _add_price_analysis(story, price, styles)


    # 5. News analysis
    _add_news_analysis(story, news, styles)

    # 6. Financial intelligence
    _add_financial_intelligence(
        story,
        intelligence,
        styles,
    )

    # 7. Overall risks
    _add_bullet_section(
        story,
        "Overall Risks and Limitations",
        data.get("risks_and_limitations", []),
        styles,
    )

    # 8. Investment assessment
    _add_heading(story, "Investment Assessment", styles)

    recommendation = data.get(
        "recommendation",
        "NOT_ASSESSED",
    )
    if isinstance(recommendation, Enum):
        recommendation = recommendation.value
    
    _add_paragraph(
        story,
        f"Recommendation status: {recommendation}",
        styles,
    )

    if recommendation == "NOT_ASSESSED":
        _add_paragraph(
            story,
            "No BUY, HOLD or SELL recommendation has been assessed "
            "by the current analysis pipeline.",
            styles,
        )

    # 9. Disclaimer
    _add_heading(story, "Disclaimer", styles)

    disclaimer = (
        "This report is generated using automated financial data "
        "retrieval and AI-assisted analysis. Information may be "
        "incomplete, delayed, or subject to source limitations. "
        "Publisher registration and metadata completeness do not "
        "establish the factual accuracy of an article's claims. "
        "This report is for informational and research purposes only "
        "and does not constitute financial advice."
    )

    _add_paragraph(story, disclaimer, styles)

    document.build(
        story,
        onFirstPage=_add_page_number,
        onLaterPages=_add_page_number,
    )

    if output_path:
        return output_path

    return buffer.getvalue()
