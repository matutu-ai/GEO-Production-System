"""Complete GEO analysis pipeline."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

from ..agents.article_analyzer import ArticleAnalyzerAgent
from ..agents.entity_agent import EntityAgent
from ..agents.framework_agent import FrameworkAgent
from ..agents.intent_agent import IntentAgent
from ..agents.keyword_agent import KeywordAgent
from ..agents.svg_agent import SVGAgent
from ..exporters.export_service import export_all
from ..schemas.geo_schema import GEOAnalysisResult, GEOScore

LOGGER = logging.getLogger(__name__)

ProgressCallback = Callable[[str, int], None]


class GEOAnalysisPipeline:
    """Run the six GEO analysis agents and export the report package."""

    def __init__(self, output_dir: Optional[Path] = None) -> None:
        root = Path(__file__).resolve().parents[2]
        self.output_dir = Path(output_dir or root / "storage" / "geo_analysis" / "exports")

    def run(
        self,
        project_id: str,
        input_data: Dict[str, Any],
        progress_callback: Optional[ProgressCallback] = None,
    ) -> Dict[str, Any]:
        """Execute the full pipeline and return the analysis result."""
        self._notify(progress_callback, "ANALYZING", 10)
        article_result = ArticleAnalyzerAgent().run(input_data)
        self._ensure_success(article_result, "Article Analyzer")
        article = article_result["result"]
        self._notify(progress_callback, "ANALYZING", 25)

        entity_input = {"article": article, "input_data": input_data}
        entity_result = EntityAgent().run(entity_input)
        self._ensure_success(entity_result, "Entity Analysis")
        entities = entity_result["result"]
        self._notify(progress_callback, "ANALYZING", 40)

        keyword_input = {
            "article": article,
            "entities": entities,
            "input_data": input_data,
        }
        keyword_result = KeywordAgent().run(keyword_input)
        self._ensure_success(keyword_result, "Keyword Cluster Analysis")
        keyword_clusters = keyword_result["result"]
        self._notify(progress_callback, "ANALYZING", 55)

        intent_result = IntentAgent().run({"keyword_clusters": keyword_clusters})
        self._ensure_success(intent_result, "Search Intent Analysis")
        intents = intent_result["result"]
        self._notify(progress_callback, "GENERATING", 70)

        framework_result = FrameworkAgent().run(
            {
                "article": article,
                "keyword_clusters": keyword_clusters,
                "intents": intents,
            }
        )
        self._ensure_success(framework_result, "Content Framework Generation")
        framework = framework_result["result"]
        score = self._calculate_score(article, entities, keyword_clusters, intents, framework)
        self._notify(progress_callback, "GENERATING", 80)

        svg_result = SVGAgent().run(
            {
                "article": article,
                "framework": framework,
                "keyword_clusters": keyword_clusters,
                "intents": intents,
            }
        )
        self._ensure_success(svg_result, "SVG Architecture Generation")
        svg = svg_result["result"]["svg"]
        self._notify(progress_callback, "GENERATING", 88)

        export_dir = self.output_dir / project_id
        result = GEOAnalysisResult(
            article=article,
            entities=entities,
            keyword_clusters=keyword_clusters,
            intents=intents,
            framework=framework,
            score=score,
        ).model_dump()
        files = export_all(result, svg, export_dir)
        result["files"] = files
        svg_file = str(export_dir / "architecture.svg")
        self._notify(progress_callback, "COMPLETED", 100)
        return {
            "status": "success",
            "result": result,
            "svg_file": svg_file,
            "files": files,
        }

    @staticmethod
    def _notify(callback: Optional[ProgressCallback], stage: str, progress: int) -> None:
        if callback:
            try:
                callback(stage, progress)
            except Exception:
                LOGGER.exception("progress callback failed")

    @staticmethod
    def _ensure_success(result: Dict[str, Any], stage: str) -> None:
        if result.get("status") != "success":
            message = result.get("message", f"{stage} failed")
            raise RuntimeError(message)

    @staticmethod
    def _calculate_score(
        article: Dict[str, Any],
        entities: Dict[str, Any],
        keyword_clusters: list,
        intents: list,
        framework: Dict[str, Any],
    ) -> GEOScore:
        entity_list = entities.get("entities", []) or []
        entity_coverage = min(100, len(entity_list) * 12 + (60 if entity_list else 0))
        keyword_count = sum(len(item.get("keywords", []) or []) for item in keyword_clusters)
        keyword_coverage = min(100, 35 + len(keyword_clusters) * 8 + keyword_count * 2)
        intent_coverage = len([item for item in intents if item.get("share", 0) > 0])
        intent_match = min(100, 30 + intent_coverage * 15 + len(intents) * 5)
        structure = framework.get("structure", []) or []
        faq = framework.get("faq", []) or []
        content_structure = min(100, 20 + len(structure) * 7 + len(faq) * 6 + (12 if framework.get("schema") else 0))
        authority_score = min(
            100,
            (15 if article.get("source") else 0)
            + (20 if article.get("title") else 0)
            + (25 if article.get("summary") else 0)
            + min(40, len(framework.get("recommendations", []) or []) * 5),
        )
        total = round(
            (
                entity_coverage
                + keyword_coverage
                + intent_match
                + content_structure
                + authority_score
            )
            / 5
        )
        return GEOScore(
            entity_coverage=entity_coverage,
            keyword_coverage=keyword_coverage,
            intent_match=intent_match,
            content_structure=content_structure,
            authority_score=authority_score,
            total=total,
        )
