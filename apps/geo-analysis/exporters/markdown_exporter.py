"""Markdown report exporter."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

LOGGER = logging.getLogger(__name__)


def export_markdown(result: Dict[str, Any], output_path: Path) -> Path:
    """Write a readable GEO analysis report in Markdown."""
    article = result.get("article", {}) or {}
    entities = result.get("entities", {}) or {}
    keyword_clusters = result.get("keyword_clusters", []) or []
    intents = result.get("intents", []) or []
    framework = result.get("framework", {}) or {}
    score = result.get("score", {}) or {}

    lines = [
        f"# {article.get('title') or 'GEO Analysis Report'}",
        "",
        "## Project Overview",
        "",
        f"- Source: {article.get('source') or '-'}",
        f"- Summary: {article.get('summary') or '-'}",
        "",
        "## GEO Score",
        "",
        f"- Entity Coverage: {score.get('entity_coverage', 0)}/100",
        f"- Keyword Coverage: {score.get('keyword_coverage', 0)}/100",
        f"- Intent Match: {score.get('intent_match', 0)}/100",
        f"- Content Structure: {score.get('content_structure', 0)}/100",
        f"- Authority Score: {score.get('authority_score', 0)}/100",
        f"- Total: {score.get('total', 0)}/100",
        "",
        "## Entity Graph",
        "",
        "| Entity | Type | Confidence |",
        "| --- | --- | ---: |",
    ]
    for entity in entities.get("entities", [])[:12]:
        lines.append(f"| {entity.get('name', '')} | {entity.get('type', '')} | {entity.get('confidence', 0)} |")

    lines.extend(["", "## Keyword Clusters", ""])
    for cluster in keyword_clusters[:6]:
        lines.extend(
            [
                f"### {cluster.get('cluster', 'Keyword Cluster')}",
                "",
                f"Primary: {', '.join(cluster.get('primary', []) or [])}",
                f"Secondary: {', '.join(cluster.get('secondary', []) or [])}",
                f"Semantic: {', '.join(cluster.get('semantic', []) or [])}",
                "",
            ]
        )

    lines.extend(["## Search Intent Map", ""])
    for intent in intents[:6]:
        lines.append(
            f"- **{intent.get('label') or intent.get('intent')}**: "
            f"{intent.get('share', 0)}% - {intent.get('description')}"
        )

    lines.extend(["", "## Content Framework", ""])
    for section in framework.get("structure", [])[:10]:
        heading = section.get("heading", "")
        prefix = "#" * min(int(section.get("level", 2)), 6)
        lines.append(f"{prefix} {heading}")
        if section.get("purpose"):
            lines.append(f"_{section['purpose']}_")
        lines.append("")

    lines.extend(["## FAQ", ""])
    for item in framework.get("faq", [])[:6]:
        lines.append(f"- **{item.get('question', '')}**")
        lines.append(f"  {item.get('answer', '')}")

    lines.extend(["", "## Recommendations", ""])
    for recommendation in framework.get("recommendations", [])[:8]:
        lines.append(f"- {recommendation}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    LOGGER.info("Markdown report written: %s", output_path)
    return output_path
