"""Monitoring Agent: summarize GEO execution status and next actions."""

from __future__ import annotations

from typing import Any, Dict, List


class MonitorAgent:
    task = "geo_monitoring"

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            company = self._body(input_data.get("company_profile") or {})
            keyword_result = self._body(input_data.get("keyword_result") or {})
            persona_result = self._body(input_data.get("persona_result") or {})
            content_result = self._body(input_data.get("content_result") or {})
            strategy_result = self._body(input_data.get("strategy_result") or {})

            keywords = keyword_result.get("keywords", [])
            personas = persona_result.get("personas", [])
            content_directions = content_result.get("content_directions", [])
            faq_list = content_result.get("faq_list", [])
            case_list = content_result.get("case_list", [])
            actions = strategy_result.get("priority_actions", [])

            keyword_count = len(keywords)
            content_count = (
                len(content_directions) + len(faq_list) + len(case_list)
            )
            result: Dict[str, Any] = {
                "project_name": company.get("company_name")
                or input_data.get("customer_name", ""),
                "keyword_count": keyword_count,
                "content_count": content_count,
                "persona_count": len(personas),
                "priority_action_count": len(actions),
                "optimization_suggestions": self._suggestions(
                    keyword_count,
                    content_count,
                    len(personas),
                    content_directions,
                ),
                "next_actions": self._next_actions(
                    keyword_count,
                    content_count,
                    actions,
                ),
                "monitor_summary": self._summary(
                    keyword_count,
                    content_count,
                    len(personas),
                    len(actions),
                ),
            }
            return {
                "task": self.task,
                "status": "success",
                "confidence": min(100, 70 + min(keyword_count, 10) + min(content_count, 5)),
                "result": result,
                "next_action": "score_evaluation",
            }
        except Exception as exc:  # pragma: no cover - defensive error boundary
            return self._error(str(exc))

    def _body(self, item: Any) -> Dict[str, Any]:
        if isinstance(item, dict) and "result" in item:
            return item.get("result", {}) or {}
        return item or {}

    def _suggestions(
        self,
        keyword_count: int,
        content_count: int,
        persona_count: int,
        content_directions: List[Dict[str, Any]],
    ) -> List[str]:
        suggestions = []
        if keyword_count < 20:
            suggestions.append("扩充关键词库，覆盖品牌词、业务词、问答词、场景词和长尾词。")
        if content_count < 30:
            suggestions.append("增加官网文章、FAQ、案例和知乎问题的内容覆盖。")
        if persona_count < 4:
            suggestions.append("补全老板、采购、技术负责人、实际使用人员四类用户画像。")
        if not content_directions:
            suggestions.append("为每条业务线建立独立内容方向，并绑定目标关键词。")
        if not suggestions:
            suggestions.append("保持内容更新频率，定期补充新的客户案例和行业场景。")
        return suggestions

    def _next_actions(
        self,
        keyword_count: int,
        content_count: int,
        actions: List[Dict[str, Any]],
    ) -> List[str]:
        next_actions = []
        if keyword_count < 20:
            next_actions.append("完成关键词矩阵扩充与优先级标注。")
        if content_count < 30:
            next_actions.append("启动30天内容计划，优先发布P1关键词相关内容。")
        if actions:
            p1_actions = [
                item.get("action", "")
                for item in actions
                if item.get("priority") == "P1"
            ]
            next_actions.extend(p1_actions[:3])
        next_actions.append("每月运行GEO验证，检查AI搜索中的品牌出现率与推荐原因。")
        return next_actions[:6]

    def _summary(
        self,
        keyword_count: int,
        content_count: int,
        persona_count: int,
        action_count: int,
    ) -> str:
        return (
            f"当前已生成 {keyword_count} 个GEO关键词、{content_count} 个内容方向、"
            f"{persona_count} 类用户画像和 {action_count} 个策略动作，"
            "建议按P1动作优先落地内容与验证。"
        )

    def _error(self, message: str) -> Dict[str, Any]:
        return {
            "task": self.task,
            "status": "error",
            "confidence": 0,
            "result": {},
            "next_action": "fix_monitoring",
            "message": message,
        }

