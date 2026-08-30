"""Content framework generation agent."""

from __future__ import annotations

import json
import logging

from ..schemas.article_schema import ContentFramework, FrameworkSection

LOGGER = logging.getLogger(__name__)


class FrameworkAgent:
    """Generate a content architecture from the GEO analysis results."""

    def run(self, input_data: dict) -> dict:
        try:
            article = input_data.get("article", {}) or {}
            keyword_clusters = input_data.get("keyword_clusters", []) or []
            intents = input_data.get("intents", []) or []
            title = article.get("title") or "GEO Content Strategy"
            clusters = [cluster.get("cluster", "") for cluster in keyword_clusters if cluster.get("cluster")]
            structure = self._build_structure(title, clusters)
            faq = self._build_faq(title, clusters)
            recommendations = self._build_recommendations(intents, clusters)
            schema = self._build_schema(title, faq)
            framework = ContentFramework(
                structure=structure,
                faq=faq,
                schema=schema,
                recommendations=recommendations,
            )
            return {
                "task": "framework_generation",
                "status": "success",
                "confidence": 90,
                "result": framework.model_dump(by_alias=True),
                "next_action": "svg_generation",
            }
        except Exception as exc:
            LOGGER.exception("FrameworkAgent failed")
            return {
                "task": "framework_generation",
                "status": "error",
                "confidence": 0,
                "result": {},
                "next_action": "fix_input",
                "message": str(exc),
            }

    @staticmethod
    def _build_structure(title: str, clusters: list) -> list:
        structure = [
            FrameworkSection(heading=f"{title}: Overview", level=1, purpose="State the core topic and value proposition."),
            FrameworkSection(heading="What is GEO", level=2, purpose="Explain generative engine optimization for AI search."),
            FrameworkSection(heading="Entity Context", level=2, purpose="Cover brand, product and organization entities."),
        ]
        for index, cluster in enumerate(clusters[:4], start=1):
            structure.append(
                FrameworkSection(
                    heading=f"{index}. {cluster}",
                    level=2,
                    purpose="Address a keyword cluster with structured, authoritative content.",
                )
            )
        structure.extend(
            [
                FrameworkSection(heading="Comparison and Decision Support", level=2, purpose="Serve commercial and transactional search intent."),
                FrameworkSection(heading="FAQ", level=2, purpose="Capture question-style queries and featured answer opportunities."),
                FrameworkSection(heading="Implementation Roadmap", level=2, purpose="Turn recommendations into actionable content tasks."),
            ]
        )
        return structure

    @staticmethod
    def _build_faq(title: str, clusters: list) -> list:
        faq = [
            {
                "question": f"What is the best way to make {title} visible in AI search?",
                "answer": "Use clear entity definitions, structured headings, comparison content and FAQ answers around the core topic.",
            },
            {
                "question": "Which keywords should the content target?",
                "answer": "Target primary brand and product terms first, then support them with semantic and question-based keywords.",
            },
        ]
        for cluster in clusters[:2]:
            faq.append(
                {
                    "question": f"How does {cluster} affect GEO performance?",
                    "answer": "Cover the topic with dedicated sections, examples, citations and related entity references.",
                }
            )
        return faq

    @staticmethod
    def _build_recommendations(intents: list, clusters: list) -> list:
        recommendations = [
            "Publish one authority page per keyword cluster with a clear H1 and entity-rich body copy.",
            "Add FAQ sections to capture question-based AI search queries.",
            "Include comparison and decision content to cover commercial intent.",
        ]
        for intent in intents:
            label = intent.get("label", intent.get("intent", ""))
            recommendations.append(f"Add dedicated assets for {label} intent queries.")
        if clusters:
            recommendations.append(f"Build internal links between the top clusters: {', '.join(clusters[:4])}.")
        return recommendations[:8]

    @staticmethod
    def _build_schema(title: str, faq: list) -> str:
        payload = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title,
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": "https://example.com/geo-article",
            },
            "about": {
                "@type": "Thing",
                "name": "Generative Engine Optimization",
            },
        }
        if faq:
            payload["mainEntity"] = [
                {
                    "@type": "Question",
                    "name": item["question"],
                    "acceptedAnswer": {"@type": "Answer", "text": item["answer"]},
                }
                for item in faq
            ]
        return json.dumps(payload, ensure_ascii=False, indent=2)
