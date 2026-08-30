"""HTML report exporter."""

from __future__ import annotations

import html
import json
import logging
from pathlib import Path
from typing import Any, Dict

LOGGER = logging.getLogger(__name__)


def export_html(result: Dict[str, Any], svg: str, output_path: Path) -> Path:
    """Write a standalone HTML report with embedded SVG."""
    article = result.get("article", {}) or {}
    entities = result.get("entities", {}) or {}
    keyword_clusters = result.get("keyword_clusters", []) or []
    intents = result.get("intents", []) or []
    framework = result.get("framework", {}) or {}
    score = result.get("score", {}) or {}

    entity_rows = "\n".join(
        f"<tr><td>{html.escape(str(item.get('name', '')))}</td>"
        f"<td>{html.escape(str(item.get('type', '')))}</td>"
        f"<td>{int(item.get('confidence', 0))}</td></tr>"
        for item in entities.get("entities", [])[:12]
    )
    cluster_html = ""
    for cluster in keyword_clusters[:6]:
        cluster_html += (
            f"<section class='card'><h3>{html.escape(str(cluster.get('cluster', '')))}</h3>"
            f"<p><strong>Primary:</strong> {html.escape(', '.join(cluster.get('primary', []) or []))}</p>"
            f"<p><strong>Secondary:</strong> {html.escape(', '.join(cluster.get('secondary', []) or []))}</p>"
            f"<p><strong>Semantic:</strong> {html.escape(', '.join(cluster.get('semantic', []) or []))}</p></section>"
        )
    intent_html = "".join(
        f"<span class='tag'>{html.escape(str(item.get('label') or item.get('intent')))} {int(item.get('share', 0))}%</span>"
        for item in intents[:6]
    )
    structure_html = "".join(
        f"<li><strong>{html.escape(str(item.get('heading', '')))}</strong><p>{html.escape(str(item.get('purpose', '')))}</p></li>"
        for item in framework.get("structure", [])[:10]
    )
    faq_html = "".join(
        f"<li><strong>{html.escape(str(item.get('question', '')))}</strong>"
        f"<p>{html.escape(str(item.get('answer', '')))}</p></li>"
        for item in framework.get("faq", [])[:6]
    )
    recommendation_html = "".join(
        f"<li>{html.escape(str(item))}</li>" for item in framework.get("recommendations", [])[:8]
    )

    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(str(article.get('title') or 'GEO Analysis Report'))}</title>
  <style>
    body {{ margin: 0; background: #f5f7fb; color: #17233d; font-family: -apple-system, "Segoe UI", "PingFang SC", sans-serif; }}
    .shell {{ max-width: 1200px; margin: 0 auto; padding: 28px; }}
    h1 {{ font-size: 32px; margin-bottom: 8px; }}
    h2 {{ margin-top: 28px; border-bottom: 2px solid #e5e9f0; padding-bottom: 8px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; }}
    .score {{ background: #fff; border: 1px solid #e5e9f0; border-radius: 10px; padding: 16px; }}
    .score strong {{ display: block; font-size: 24px; color: #1f5eff; }}
    .card {{ background: #fff; border: 1px solid #e5e9f0; border-radius: 10px; padding: 16px; margin: 12px 0; }}
    .tag {{ display: inline-block; background: #eef4ff; color: #1f5eff; border-radius: 999px; padding: 4px 10px; margin: 4px; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; }}
    th, td {{ border: 1px solid #e5e9f0; padding: 8px 10px; text-align: left; }}
    th {{ background: #f0f5ff; }}
    .svg-shell {{ background: #fff; border: 1px solid #e5e9f0; border-radius: 12px; padding: 16px; margin: 20px 0; }}
  </style>
</head>
<body>
  <main class="shell">
    <h1>{html.escape(str(article.get('title') or 'GEO Analysis Report'))}</h1>
    <p>{html.escape(str(article.get('summary') or ''))}</p>
    <section>
      <h2>GEO Score</h2>
      <div class="grid">
        <div class="score"><strong>{int(score.get('entity_coverage', 0))}</strong>Entity Coverage</div>
        <div class="score"><strong>{int(score.get('keyword_coverage', 0))}</strong>Keyword Coverage</div>
        <div class="score"><strong>{int(score.get('intent_match', 0))}</strong>Intent Match</div>
        <div class="score"><strong>{int(score.get('content_structure', 0))}</strong>Content Structure</div>
        <div class="score"><strong>{int(score.get('authority_score', 0))}</strong>Authority Score</div>
        <div class="score"><strong>{int(score.get('total', 0))}</strong>Total</div>
      </div>
    </section>
    <section>
      <h2>Architecture</h2>
      <div class="svg-shell">{svg}</div>
    </section>
    <section>
      <h2>Entity Graph</h2>
      <table><thead><tr><th>Entity</th><th>Type</th><th>Confidence</th></tr></thead><tbody>{entity_rows}</tbody></table>
    </section>
    <section>
      <h2>Keyword Clusters</h2>{cluster_html}
    </section>
    <section>
      <h2>Search Intent Map</h2>{intent_html}
    </section>
    <section>
      <h2>Content Framework</h2><ol>{structure_html}</ol>
    </section>
    <section>
      <h2>FAQ</h2><ul>{faq_html}</ul>
    </section>
    <section>
      <h2>Recommendations</h2><ul>{recommendation_html}</ul>
    </section>
  </main>
</body>
</html>
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(page, encoding="utf-8")
    LOGGER.info("HTML report written: %s", output_path)
    return output_path
