"""GEO Score Agent: quantifies project readiness for AI search visibility."""

from __future__ import annotations

from typing import Any, Dict, List


class ScoreAgent:
    task = "geo_score"

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            company = self._body(input_data.get("company_profile") or {})
            keywords = self._body(input_data.get("keyword_result") or {}).get(
                "keywords", []
            )
            personas = self._body(input_data.get("persona_result") or {}).get(
                "personas", []
            )
            content = self._body(input_data.get("content_result") or {})
            monitor = self._body(input_data.get("monitor_result") or {})

            dimensions = {
                "enterprise_info_completeness": self._enterprise_score(company),
                "keyword_coverage": self._keyword_score(keywords),
                "content_coverage": self._content_score(content),
                "persona_completeness": self._persona_score(personas),
                "ai_recommendation_foundation": self._ai_foundation_score(
                    company, monitor
                ),
            }
            total = round(sum(dimensions.values()) / len(dimensions), 1)
            level = (
                "excellent"
                if total >= 90
                else "good"
                if total >= 75
                else "medium"
                if total >= 60
                else "needs_improvement"
            )
            recommendations = self._recommendations(
                dimensions, keywords, personas, content
            )
            return {
                "task": self.task,
                "status": "success",
                "confidence": 100,
                "result": {
                    "score": total,
                    "level": level,
                    "dimensions": dimensions,
                    "recommendations": recommendations,
                },
                "next_action": "report_generation",
            }
        except Exception as exc:  # pragma: no cover - defensive error boundary
            return self._error(str(exc))

    def _body(self, item: Any) -> Dict[str, Any]:
        if isinstance(item, dict) and "result" in item:
            return item.get("result", {}) or {}
        return item or {}

    def _enterprise_score(self, company: Dict[str, Any]) -> float:
        checks = [
            bool(company.get("company_positioning")),
            bool(company.get("industry")),
            bool(company.get("products")),
            bool(company.get("target_customers")),
            bool(company.get("advantages")),
            bool(company.get("evidence")),
        ]
        return round(sum(checks) / len(checks) * 100, 1)

    def _keyword_score(self, keywords: List[Dict[str, Any]]) -> float:
        if not keywords:
            return 0
        has_priority = sum(1 for item in keywords if item.get("priority"))
        has_intent = sum(1 for item in keywords if item.get("intent"))
        coverage = min(100, (len(keywords) / 30) * 100)
        quality = (
            (has_priority / len(keywords)) * 0.5
            + (has_intent / len(keywords)) * 0.5
        ) * 100
        return round(coverage * 0.4 + quality * 0.6, 1)

    def _content_score(self, content: Dict[str, Any]) -> float:
        counts = [
            len(content.get("content_directions", [])),
            len(content.get("faq_list", [])),
            len(content.get("case_list", [])),
            len(content.get("plan", [])),
        ]
        total = sum(counts)
        if total == 0:
            return 0
        return round(min(100, 40 + total * 2), 1)

    def _persona_score(self, personas: List[Dict[str, Any]]) -> float:
        if not personas:
            return 0
        completeness = 0
        for persona in personas:
            fields = [
                "role",
                "focus",
                "pain_points",
                "search_behavior",
                "decision_factors",
                "content_needs",
            ]
            completeness += sum(
                1 for field_name in fields if persona.get(field_name)
            ) / len(fields)
        return round(
            min(100, (completeness / len(personas)) * 100 + len(personas) * 3),
            1,
        )

    def _ai_foundation_score(
        self, company: Dict[str, Any], monitor: Dict[str, Any]
    ) -> float:
        score = 30.0
        if company.get("evidence"):
            score += 20
        if monitor.get("priority_action_count", 0) >= 3:
            score += 20
        if monitor.get("next_actions"):
            score += 15
        if company.get("company_positioning"):
            score += 15
        return round(min(100, score), 1)

    def _recommendations(
        self,
        dimensions: Dict[str, float],
        keywords: List[Dict[str, Any]],
        personas: List[Dict[str, Any]],
        content: Dict[str, Any],
    ) -> List[str]:
        recommendations = []
        low_items = [
            (label, value)
            for label, value in dimensions.items()
            if value < 70
        ]
        labels = {
            "enterprise_info_completeness": "企业信息完整度",
            "keyword_coverage": "关键词覆盖度",
            "content_coverage": "内容覆盖度",
            "persona_completeness": "用户画像完整度",
            "ai_recommendation_foundation": "AI推荐基础能力",
        }
        for key, value in low_items:
            recommendations.append(f"{labels.get(key, key)}仅 {value} 分，需优先补齐。")
        if len(keywords) < 30:
            recommendations.append("将关键词矩阵扩充到30条以上，并覆盖问答词和场景词。")
        if len(personas) < 4:
            recommendations.append("补全至少4类用户画像，明确搜索行为与决策因素。")
        if not content.get("case_list"):
            recommendations.append("增加客户案例内容，为AI回答提供可信证据。")
        return recommendations[:8]

    def _error(self, message: str) -> Dict[str, Any]:
        return {
            "task": self.task,
            "status": "error",
            "confidence": 0,
            "result": {
                "score": 0,
                "level": "needs_improvement",
                "dimensions": {},
                "recommendations": [],
            },
            "next_action": "fix_scoring",
            "message": message,
        }
