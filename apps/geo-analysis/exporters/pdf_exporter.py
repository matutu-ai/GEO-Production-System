"""PDF report exporter."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

LOGGER = logging.getLogger(__name__)

try:
    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    DEFAULT_FONT = "STSong-Light"
except Exception:
    DEFAULT_FONT = "Helvetica"


def export_pdf(result: Dict[str, Any], output_path: Path) -> Path:
    """Write a paginated PDF GEO analysis report."""
    article = result.get("article", {}) or {}
    entities = result.get("entities", {}) or {}
    keyword_clusters = result.get("keyword_clusters", []) or []
    intents = result.get("intents", []) or []
    framework = result.get("framework", {}) or {}
    score = result.get("score", {}) or {}

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=str(article.get("title") or "GEO Analysis Report"),
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "GeoTitle",
        parent=styles["Title"],
        fontName=DEFAULT_FONT,
        fontSize=22,
        leading=28,
        spaceAfter=8,
    )
    heading_style = ParagraphStyle(
        "GeoHeading",
        parent=styles["Heading2"],
        fontName=DEFAULT_FONT,
        fontSize=15,
        leading=20,
        spaceBefore=14,
        spaceAfter=6,
        textColor=colors.HexColor("#1f5eff"),
    )
    body_style = ParagraphStyle(
        "GeoBody",
        parent=styles["BodyText"],
        fontName=DEFAULT_FONT,
        fontSize=10,
        leading=15,
    )
    small_style = ParagraphStyle(
        "GeoSmall",
        parent=body_style,
        fontSize=8,
        leading=12,
    )

    story = [
        Paragraph(str(article.get("title") or "GEO Analysis Report"), title_style),
        Paragraph(str(article.get("summary") or ""), body_style),
        Spacer(1, 8),
    ]
    story.extend(
        [
            Paragraph("GEO Score", heading_style),
            _table(
                [
                    ["Entity Coverage", "Keyword Coverage", "Intent Match", "Content Structure", "Authority Score", "Total"],
                    [
                        score.get("entity_coverage", 0),
                        score.get("keyword_coverage", 0),
                        score.get("intent_match", 0),
                        score.get("content_structure", 0),
                        score.get("authority_score", 0),
                        score.get("total", 0),
                    ],
                ],
                body_style,
            ),
        ]
    )

    story.append(PageBreak())
    story.append(Paragraph("Entity Graph", heading_style))
    entity_rows = [["Entity", "Type", "Confidence"]]
    entity_rows.extend(
        [
            [str(item.get("name", "")), str(item.get("type", "")), str(item.get("confidence", 0))]
            for item in entities.get("entities", [])[:12]
        ]
    )
    story.append(_table(entity_rows, body_style))

    story.append(Paragraph("Keyword Clusters", heading_style))
    for cluster in keyword_clusters[:6]:
        story.append(Paragraph(str(cluster.get("cluster", "")), body_style))
        story.append(
            Paragraph(
                f"Primary: {', '.join(cluster.get('primary', []) or [])}<br/>"
                f"Secondary: {', '.join(cluster.get('secondary', []) or [])}<br/>"
                f"Semantic: {', '.join(cluster.get('semantic', []) or [])}",
                small_style,
            )
        )
        story.append(Spacer(1, 6))

    story.append(Paragraph("Search Intent Map", heading_style))
    intent_rows = [["Intent", "Share", "Description"]]
    intent_rows.extend(
        [
            [
                str(item.get("label") or item.get("intent", "")),
                f"{int(item.get('share', 0))}%",
                str(item.get("description", "")),
            ]
            for item in intents[:6]
        ]
    )
    story.append(_table(intent_rows, small_style))

    story.append(PageBreak())
    story.append(Paragraph("Content Framework", heading_style))
    for section in framework.get("structure", [])[:10]:
        story.append(Paragraph(str(section.get("heading", "")), body_style))
        if section.get("purpose"):
            story.append(Paragraph(str(section["purpose"]), small_style))

    story.append(Paragraph("FAQ", heading_style))
    for item in framework.get("faq", [])[:6]:
        story.append(Paragraph(f"Q: {item.get('question', '')}", body_style))
        story.append(Paragraph(f"A: {item.get('answer', '')}", small_style))

    story.append(Paragraph("Recommendations", heading_style))
    for recommendation in framework.get("recommendations", [])[:8]:
        story.append(Paragraph(f"- {recommendation}", small_style))

    doc.build(story)
    LOGGER.info("PDF report written: %s", output_path)
    return output_path


def _table(rows: list, style: ParagraphStyle):
    table = Table(rows, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef4ff")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d9e2f3")),
                ("FONTNAME", (0, 0), (-1, -1), style.fontName),
                ("FONTSIZE", (0, 0), (-1, -1), min(style.fontSize, 9)),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table
