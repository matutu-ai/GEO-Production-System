"""Search intent analysis agent."""

from __future__ import annotations

import logging

from ..schemas.article_schema import SearchIntent

LOGGER = logging.getLogger(__name__)

INTENT_DEFINITIONS = {
    "informational": {
        "label": "Information",
        "description": "Users look for answers, concepts, definitions and how-to guidance.",
    },
    "commercial": {
        "label": "Commercial",
        "description": "Users compare products, vendors, alternatives and expert recommendations.",
    },
    "transactional": {
        "label": "Transactional",
        "description": "Users are ready to buy, request a quote, book a demo or contact the seller.",
    },
    "navigational": {
        "label": "Navigational",
        "description": "Users search for a specific brand, website, login or official resource.",
    },
}


class IntentAgent:
    """Classify generated keywords by search intent and build an intent map."""

    def run(self, input_data: dict) -> dict:
        try:
            keyword_clusters = input_data.get("keyword_clusters", []) or []
            keywords = []
            for cluster in keyword_clusters:
                keywords.extend(cluster.get("keywords", []) if isinstance(cluster, dict) else cluster.model_dump().get("keywords", []))

            grouped = {intent: [] for intent in INTENT_DEFINITIONS}
            for keyword in keywords:
                intent = keyword.get("intent", "informational")
                grouped.setdefault(intent, []).append(keyword.get("keyword", ""))

            if not any(grouped.values()):
                grouped["informational"] = ["GEO strategy", "AI search visibility", "content framework"]

            total = sum(len(values) for values in grouped.values())
            intents = []
            for intent, definition in INTENT_DEFINITIONS.items():
                items = grouped[intent]
                share = round(len(items) / total * 100) if total else 0
                intents.append(
                    SearchIntent(
                        intent=intent,
                        label=definition["label"],
                        description=definition["description"],
                        keywords=[item for item in items if item][:8],
                        share=share,
                    ).model_dump()
                )
            return {
                "task": "intent_analysis",
                "status": "success",
                "confidence": 86,
                "result": intents,
                "next_action": "framework_generation",
            }
        except Exception as exc:
            LOGGER.exception("IntentAgent failed")
            return {
                "task": "intent_analysis",
                "status": "error",
                "confidence": 0,
                "result": [],
                "next_action": "fix_input",
                "message": str(exc),
            }
