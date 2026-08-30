"""Persona Agent: company profile -> buyer personas."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from file_writer import write_docx

BASE_DIR = Path(__file__).resolve().parents[1]


class PersonaAgent:
    task = "persona_analysis"

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        profile = input_data.get("result", input_data)
        output_dir = Path(input_data.get("output_dir", BASE_DIR / "output"))
        industry = profile.get("industry", "")
        products = profile.get("products", [])

        personas = [
            self._boss(industry),
            self._procurement(industry),
            self._technical(industry, products),
            self._operator(products),
        ]
        sections = []
        for persona in personas:
            sections.append((persona["role"], self._persona_lines(persona)))
        file_path = write_docx(output_dir / "persona_report.docx", "GEO用户画像报告", sections)

        return {
            "task": self.task,
            "status": "success",
            "result": {
                "personas": personas,
                "files": [str(file_path)],
            },
            "next_action": "content_planning",
        }

    def _boss(self, industry: str) -> Dict[str, Any]:
        return {
            "role": "老板",
            "focus": ["投入产出", "市场竞争力", "品牌增长"],
            "pain_points": ["获客依赖老客户", "品牌在AI搜索中不明显", "同行竞争加剧"],
            "search_behavior": ["搜索行业趋势", "搜索知名厂家", "比较解决方案"],
            "decision_factors": ["团队实力", "案例背书", "长期服务能力"],
            "content_needs": ["企业实力内容", "行业案例", "差异化优势"],
        }

    def _procurement(self, industry: str) -> Dict[str, Any]:
        return {
            "role": "采购负责人",
            "focus": ["价格", "交期", "供应商可靠性"],
            "pain_points": ["供应商报价不透明", "设备选型风险高", "售后保障不明"],
            "search_behavior": ["搜索厂家", "搜索报价", "搜索采购注意事项"],
            "decision_factors": ["资质", "案例", "报价", "交付周期"],
            "content_needs": ["FAQ", "报价指南", "厂家对比", "客户案例"],
        }

    def _technical(self, industry: str, products: List[str]) -> Dict[str, Any]:
        product_text = "、".join(products) if products else industry
        return {
            "role": "技术负责人",
            "focus": ["设备稳定性", "技术参数", "产线兼容性"],
            "pain_points": ["自动化方案落地难", "设备与现有产线兼容差", "定制需求沟通成本高"],
            "search_behavior": ["搜索技术方案", "搜索设备参数", "搜索实施案例"],
            "decision_factors": ["技术能力", "定制能力", "现场实施经验"],
            "content_needs": [f"{product_text}技术解析", "解决方案", "技术白皮书"],
        }

    def _operator(self, products: List[str]) -> Dict[str, Any]:
        product_text = "、".join(products) if products else "自动化设备"
        return {
            "role": "实际使用人员",
            "focus": ["操作便捷", "故障率", "培训支持"],
            "pain_points": ["设备操作复杂", "故障处理慢", "培训资料不足"],
            "search_behavior": ["搜索操作教程", "搜索常见故障", "搜索保养方法"],
            "decision_factors": ["易用性", "稳定性", "售后服务"],
            "content_needs": ["操作指南", "FAQ", "维护保养内容"],
        }

    def _persona_lines(self, persona: Dict[str, Any]) -> List[str]:
        lines = []
        lines.append(f"关注点：{'、'.join(persona['focus'])}")
        lines.append(f"痛点：{'、'.join(persona['pain_points'])}")
        lines.append(f"搜索行为：{'、'.join(persona['search_behavior'])}")
        lines.append(f"决策因素：{'、'.join(persona['decision_factors'])}")
        lines.append(f"内容需求：{'、'.join(persona['content_needs'])}")
        return lines

