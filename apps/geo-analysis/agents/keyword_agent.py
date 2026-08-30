"""Keyword cluster analysis agent."""

from __future__ import annotations

import logging

from ..schemas.article_schema import Keyword, KeywordCluster

LOGGER = logging.getLogger(__name__)


class KeywordAgent:
    """Generate primary, secondary, semantic and topic-cluster keywords."""

    def run(self, input_data: dict) -> dict:
        try:
            article = input_data.get("article", {}) or {}
            entities = input_data.get("entities", {}) or {}
            product_description = str(input_data.get("input_data", {}).get("product_description", ""))
            seed_terms = self._seed_terms(article, entities, product_description)
            clusters = self._build_clusters(seed_terms, article.get("topics", []))
            return {
                "task": "keyword_cluster_analysis",
                "status": "success",
                "confidence": 88,
                "result": clusters,
                "next_action": "intent_analysis",
            }
        except Exception as exc:
            LOGGER.exception("KeywordAgent failed")
            return {
                "task": "keyword_cluster_analysis",
                "status": "error",
                "confidence": 0,
                "result": [],
                "next_action": "fix_input",
                "message": str(exc),
            }

    def _seed_terms(self, article: dict, entities: dict, product_description: str) -> list:
        seeds = []
        for item in article.get("keywords", [])[:12]:
            seeds.append(str(item))
        for entity in entities.get("entities", [])[:8]:
            seeds.append(entity.get("name", ""))
        for item in re_split(product_description):
            seeds.append(item)
        unique = []
        for seed in seeds:
            value = seed.strip()
            if value and value not in unique:
                unique.append(value)
        return unique[:20]

    def _build_clusters(self, seeds: list, topics: list) -> list:
        clusters: list[KeywordCluster] = []
        topic_terms = [str(topic) for topic in topics[:4]] or ["GEO visibility", "brand presence", "content strategy"]
        while len(clusters) < 4:
            topic = topic_terms[len(clusters) % len(topic_terms)]
            cluster_keywords = seeds[clusters_len_seed(seeds, len(clusters)) : clusters_len_seed(seeds, len(clusters)) + 4]
            primary = cluster_keywords[:2] or [f"{topic} GEO strategy"]
            secondary = cluster_keywords[2:4] or [f"{topic} AI search visibility"]
            semantic = [
                f"{primary[0]} benefits",
                f"{primary[0]} best practices",
                f"{topic} FAQ",
            ]
            keyword_items = []
            for index, keyword in enumerate(primary + secondary + semantic[:2]):
                keyword_items.append(
                    Keyword(
                        keyword=keyword,
                        type="primary" if index < 2 else "secondary" if index < 4 else "semantic",
                        intent=self._guess_intent(keyword),
                        priority="A" if index < 2 else "B" if index < 4 else "C",
                        cluster=topic,
                    ).model_dump()
                )
            clusters.append(
                KeywordCluster(
                    cluster=topic,
                    primary=primary,
                    secondary=secondary,
                    semantic=semantic,
                    keywords=keyword_items,
                ).model_dump()
            )
        return clusters

    @staticmethod
    def _guess_intent(keyword: str) -> str:
        lowered = keyword.lower()
        if any(token in lowered for token in ("price", "buy", "purchase", "quote", "cost", "download", "sign up")):
            return "transactional"
        if any(token in lowered for token in ("vs", "review", "alternative", "best", "compare", "solution")):
            return "commercial"
        if any(token in lowered for token in ("login", "home", "official", "website")):
            return "navigational"
        return "informational"


def re_split(value: str) -> list:
    if not value:
        return []
    import re

    return [item.strip() for item in re.split(r"[\n,，;；、|]+", value) if item.strip()]


def clusters_len_seed(seeds: list, index: int) -> int:
    if not seeds:
        return index * 4
    return (index * 4) % len(seeds)
