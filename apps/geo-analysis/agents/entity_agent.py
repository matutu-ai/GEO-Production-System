"""GEO entity analysis agent."""

from __future__ import annotations

import logging
import re

from ..schemas.article_schema import Entity, EntityGraph

LOGGER = logging.getLogger(__name__)


class EntityAgent:
    """Extract brand, product, organization, location and person entities."""

    def run(self, input_data: dict) -> dict:
        try:
            article = input_data.get("article", {}) or {}
            payload = input_data.get("input_data", {}) or {}
            product_description = str(payload.get("product_description", ""))
            company_info = str(payload.get("company_info", ""))
            content = "\n".join(
                [
                    str(article.get("title", "")),
                    str(article.get("summary", "")),
                    str(article.get("content", "")),
                ]
            )
            entities: list[Entity] = []
            seen = set()

            company = self._extract_company(company_info, content, article)
            if company:
                self._add_entity(entities, seen, company, "Brand", 92)

            for product in self._extract_products(product_description, content, article):
                self._add_entity(entities, seen, product, "Product", 88)

            for org in self._extract_organizations(company_info, content):
                self._add_entity(entities, seen, org, "Organization", 80)

            for location in self._extract_locations(content):
                self._add_entity(entities, seen, location, "Location", 72)

            for person in self._extract_persons(content):
                self._add_entity(entities, seen, person, "Person", 66)

            relationships = self._build_relationships(entities)
            graph = EntityGraph(entities=entities, relationships=relationships)
            return {
                "task": "entity_analysis",
                "status": "success",
                "confidence": 85,
                "result": graph.model_dump(),
                "next_action": "keyword_cluster_analysis",
            }
        except Exception as exc:
            LOGGER.exception("EntityAgent failed")
            return {
                "task": "entity_analysis",
                "status": "error",
                "confidence": 0,
                "result": {},
                "next_action": "fix_input",
                "message": str(exc),
            }

    @staticmethod
    def _add_entity(entities, seen, name, entity_type, confidence):
        key = name.strip().lower()
        if not key or key in seen:
            return
        seen.add(key)
        entities.append(Entity(name=name.strip(), type=entity_type, confidence=confidence))

    @staticmethod
    def _extract_company(company_info: str, content: str, article: dict) -> str:
        if company_info:
            first_line = company_info.strip().splitlines()[0].strip()
            return first_line.strip(":。.").strip()
        if article.get("title"):
            return str(article["title"]).split(":")[0].split("-")[0].strip()[:60]
        match = re.search(r"([\u4e00-\u9fffA-Za-z0-9]{2,}(?:公司|集团|品牌|科技|企业))", content)
        return match.group(1) if match else "Brand Entity"

    @staticmethod
    def _extract_products(product_description: str, content: str, article: dict) -> list:
        products = []
        for item in re.split(r"[\n,，;；、|]+", product_description):
            item = item.strip()
            if item:
                products.append(item)
        patterns = [
            r"[\u4e00-\u9fffA-Za-z0-9+/-]{2,}(?:机|线|系统|设备|方案|平台|服务)",
            r"[A-Z][A-Za-z0-9+]{2,}(?:\s[A-Z][A-Za-z0-9+]{1,})?",
        ]
        for pattern in patterns:
            for match in re.findall(pattern, content):
                value = match.strip()
                if value and value not in products and len(value) < 60:
                    products.append(value)
        for topic in article.get("topics", [])[:4]:
            if topic not in products:
                products.append(str(topic))
        return products[:8]

    @staticmethod
    def _extract_organizations(company_info: str, content: str) -> list:
        candidates = []
        for match in re.findall(r"([\u4e00-\u9fffA-Za-z0-9]{2,}(?:协会|研究院|实验室|联盟|大学|部门))", content):
            if match not in candidates:
                candidates.append(match)
        for match in re.findall(r"\b([A-Z][A-Za-z0-9]{2,}(?:\s[A-Za-z0-9]{2,}){0,3})\b", content):
            if match.upper() not in {"GEO", "AI", "SEO", "PDF", "HTML", "API"}:
                candidates.append(match)
        return candidates[:5]

    @staticmethod
    def _extract_locations(content: str) -> list:
        candidates = []
        pattern = r"(?:位于|总部|在|来自)\s*([\u4e00-\u9fff]{2,10}(?:市|省|区|县|州))"
        for match in re.findall(pattern, content):
            if match not in candidates:
                candidates.append(match)
        for country in ("China", "United States", "Germany", "Japan", "Singapore"):
            if country.lower() in content.lower():
                candidates.append(country)
        return candidates[:5]

    @staticmethod
    def _extract_persons(content: str) -> list:
        candidates = []
        pattern = r"([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,2})"
        for match in re.findall(pattern, content):
            if match not in candidates and not any(word in match for word in ("The", "How", "What", "Why", "Your")):
                candidates.append(match)
        return candidates[:5]

    @staticmethod
    def _build_relationships(entities: list[Entity]) -> list:
        relationships = []
        products = [entity for entity in entities if entity.type == "Product"]
        brands = [entity for entity in entities if entity.type == "Brand"]
        for product in products[:4]:
            for brand in brands[:1]:
                relationships.append(
                    {
                        "source": brand.name,
                        "target": product.name,
                        "relation": "offers",
                    }
                )
        return relationships
