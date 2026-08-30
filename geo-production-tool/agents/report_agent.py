"""Report Agent: final GEO delivery report."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from file_writer import write_markdown

BASE_DIR = Path(__file__).resolve().parents[1]


class ReportAgent:
    task = "report_generation"

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        company = input_data.get("company_profile", {})
        keyword_result = input_data.get("keyword_result", {}).get("result", {})
        persona_result = input_data.get("persona_result", {}).get("result", {})
        content_result = input_data.get("content_result", {}).get("result", {})
        strategy_result = input_data.get("strategy_result", {}).get("result", {})
        output_dir = Path(input_data.get("output_dir", BASE_DIR / "output"))

        keywords = keyword_result.get("keywords", [])
        personas = persona_result.get("personas", [])
        plan = content_result.get("plan", [])
        strategy_actions = strategy_result.get("priority_actions", [])

        sections = [
            ("企业分析", self._company_lines(company)),
            ("GEO关键词策略", self._keyword_lines(keywords)),
            ("用户画像", self._persona_lines(personas)),
            ("30天内容计划", self._plan_lines(plan)),
            ("GEO优化策略", self._strategy_lines(strategy_actions)),
            ("交付建议", ["优先优化A级高意向关键词", "补充官网FAQ和结构化内容", "持续产出行业案例内容"]),
        ]
        file_path = write_markdown(output_dir / "GEO分析报告.md", "GEO交付方案", sections)
        files = []
        for result_key in ("keyword_result", "persona_result", "content_result"):
            files.extend(input_data.get(result_key, {}).get("result", {}).get("files", []))
        files.extend(strategy_result.get("files", []))
        files.append(str(file_path))
        return {
            "task": self.task,
            "status": "success",
            "result": {
                "files": files,
            },
            "next_action": "done",
        }

    def _company_lines(self, company: Dict[str, Any]) -> List[str]:
        return [
            f"企业定位：{company.get('company_positioning', '')}",
            f"行业：{company.get('industry', '')}",
            f"产品：{'、'.join(company.get('products', []))}",
            f"目标客户：{'、'.join(company.get('target_customers', []))}",
            f"优势：{'、'.join(company.get('advantages', []))}",
            f"证据：{'、'.join(company.get('evidence', []))}",
        ]

    def _keyword_lines(self, keywords: List[Dict[str, Any]]) -> List[str]:
        top = sorted(
            [k for k in keywords if k.get("priority") == "A"],
            key=lambda item: item.get("keyword", ""),
        )[:15]
        return [f"[{k['priority']}] {k['keyword']}（{k['type']}）" for k in top]

    def _persona_lines(self, personas: List[Dict[str, Any]]) -> List[str]:
        lines = []
        for persona in personas:
            lines.append(
                f"{persona.get('role')}：关注{'、'.join(persona.get('focus', []))}"
            )
        return lines

    def _plan_lines(self, plan: List[Dict[str, Any]]) -> List[str]:
        return [
            f"{item.get('日期')}：{item.get('内容主题')}（关键词：{item.get('目标关键词')}）"
            for item in plan[:15]
        ]

    def _strategy_lines(self, actions: List[Dict[str, Any]]) -> List[str]:
        return [
            (
                f"[{action.get('priority')}] {action.get('action')} | "
                f"原因：{action.get('reason')} | 预计价值：{action.get('expected_value', '')}"
            )
            for action in actions
        ]
