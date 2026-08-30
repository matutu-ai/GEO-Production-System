"""SVG architecture generation agent."""

from __future__ import annotations

import logging

from ..svg.renderer import render_architecture_svg

LOGGER = logging.getLogger(__name__)


class SVGAgent:
    """Generate the SVG architecture diagram for a GEO analysis project."""

    def run(self, input_data: dict) -> dict:
        try:
            framework = input_data.get("framework", {}) or {}
            article = input_data.get("article", {}) or {}
            keyword_clusters = input_data.get("keyword_clusters", []) or []
            intents = input_data.get("intents", []) or []
            svg = render_architecture_svg(
                title=article.get("title") or "GEO Analysis Architecture",
                framework=framework,
                keyword_clusters=keyword_clusters,
                intents=intents,
            )
            return {
                "task": "svg_generation",
                "status": "success",
                "confidence": 95,
                "result": {"svg": svg, "filename": "architecture.svg"},
                "next_action": "export",
            }
        except Exception as exc:
            LOGGER.exception("SVGAgent failed")
            return {
                "task": "svg_generation",
                "status": "error",
                "confidence": 0,
                "result": {},
                "next_action": "fix_input",
                "message": str(exc),
            }
