"""Knowledge Extract Agent: enterprise document -> structured knowledge."""

from __future__ import annotations

from typing import Any, Dict

from agents.knowledge_agent.extractor import KnowledgeExtractor
from agents.knowledge_agent.prompt import EXTRACTION_PROMPT, SYSTEM_PROMPT


class KnowledgeExtractAgent:
    task = "knowledge_extraction"

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            document = input_data.get("document") or {}
            document_body = document.get("document", document)
            content = document_body.get("content", "") if isinstance(document_body, dict) else ""
            raw_information = input_data.get("raw_information") or ""
            content = content or raw_information
            chunks = document.get("chunks", [])

            extractor = KnowledgeExtractor()
            knowledge = extractor.extract(content, chunks)
            profile = input_data.get("customer_profile") or {}
            merged = self._merge(profile, knowledge)
            result = {
                "knowledge_base": merged,
                "company": merged["company"],
                "products": merged["products"],
                "market": merged["market"],
                "prompt": {
                    "system": SYSTEM_PROMPT,
                    "template": EXTRACTION_PROMPT,
                },
            }
            return {
                "task": self.task,
                "status": "success",
                "confidence": self._confidence(merged),
                "result": result,
                "next_action": "company_analysis",
            }
        except Exception as exc:
            return self._error(str(exc))

    def _merge(
        self,
        profile: Dict[str, Any],
        knowledge: Dict[str, Any],
    ) -> Dict[str, Any]:
        company = dict(knowledge.get("company", {}))
        if profile.get("name") and not company.get("company_name"):
            company["company_name"] = profile["name"]
        if profile.get("website") and not company.get("website"):
            company["website"] = profile["website"]
        if profile.get("industry") and not company.get("industry"):
            company["industry"] = profile["industry"]
        company["services"] = self._dedupe(
            company.get("services", []) + (profile.get("services") or [])
        )
        company["customers"] = self._dedupe(
            company.get("customers", []) + (profile.get("customers") or [])
        )
        return {
            "company": company,
            "products": knowledge.get("products", []),
            "market": knowledge.get("market", {}),
        }

    @staticmethod
    def _dedupe(items: list) -> list:
        seen = []
        for item in items:
            if item and item not in seen:
                seen.append(item)
        return seen

    @staticmethod
    def _confidence(knowledge: Dict[str, Any]) -> int:
        company = knowledge.get("company", {})
        score = 40
        if company.get("company_name"):
            score += 20
        if company.get("industry"):
            score += 10
        if knowledge.get("products"):
            score += 20
        if knowledge.get("market"):
            score += 10
        return min(100, score)

    @staticmethod
    def _error(message: str) -> Dict[str, Any]:
        return {
            "task": "knowledge_extraction",
            "status": "error",
            "confidence": 0,
            "result": {
                "knowledge_base": {},
                "company": {},
                "products": [],
                "market": {},
            },
            "next_action": "fix_document",
            "message": message,
        }
