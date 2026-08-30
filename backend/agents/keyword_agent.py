"""Keyword Agent: business analysis -> GEO keyword matrix."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from file_writer import write_xlsx

BASE_DIR = Path(__file__).resolve().parents[1]


class KeywordAgent:
    task = "keyword_analysis"

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        profile = (
            input_data.get("company_profile")
            or input_data.get("result")
            or input_data
        )
        business = input_data.get("business_analysis", {}) or {}
        if isinstance(business, dict) and "result" in business:
            business = business.get("result", {})
        business_lines = business.get("business_lines", [])
        output_dir = Path(input_data.get("output_dir", BASE_DIR / "output"))

        name = profile.get("company_name", "")
        short_name = name.replace("有限公司", "")
        industry = profile.get("industry", "")
        keywords: List[Dict[str, str]] = []
        seen = set()

        for keyword, intent, priority in self._brand_words(name, short_name, industry):
            self._add_keyword(
                keywords,
                seen,
                keyword=keyword,
                kind="品牌词",
                intent=intent,
                priority=priority,
                business_line="企业品牌",
                customer_type="全客户",
                search_stage="认知",
            )

        for line in business_lines:
            line_name = line.get("business_name", "")
            line_products = line.get("products", [])
            customers = line.get("target_customers", [])
            customer_type = customers[0] if customers else "目标客户"
            keywords_direction = line.get("keywords_direction", [])

            for product in line_products:
                self._add_keyword(
                    keywords,
                    seen,
                    keyword=product,
                    kind="业务词",
                    intent="采购决策",
                    priority="A",
                    business_line=line_name,
                    customer_type=customer_type,
                    search_stage="决策",
                )
                self._add_keyword(
                    keywords,
                    seen,
                    keyword=f"{product}厂家",
                    kind="业务词",
                    intent="采购决策",
                    priority="A",
                    business_line=line_name,
                    customer_type=customer_type,
                    search_stage="对比",
                )
                self._add_keyword(
                    keywords,
                    seen,
                    keyword=f"{product}怎么选",
                    kind="问答词",
                    intent="信息了解",
                    priority="B",
                    business_line=line_name,
                    customer_type=customer_type,
                    search_stage="需求",
                )
                self._add_keyword(
                    keywords,
                    seen,
                    keyword=f"{product}多少钱",
                    kind="问答词",
                    intent="价格对比",
                    priority="A",
                    business_line=line_name,
                    customer_type=customer_type,
                    search_stage="对比",
                )
                for customer in customers[:2]:
                    self._add_keyword(
                        keywords,
                        seen,
                        keyword=f"{customer}{product}",
                        kind="场景词",
                        intent="场景需求",
                        priority="A",
                        business_line=line_name,
                        customer_type=customer,
                        search_stage="需求",
                    )
                self._add_keyword(
                    keywords,
                    seen,
                    keyword=f"支持定制的{product}厂家",
                    kind="长尾词",
                    intent="高意向采购",
                    priority="A",
                    business_line=line_name,
                    customer_type=customer_type,
                    search_stage="决策",
                )
                self._add_keyword(
                    keywords,
                    seen,
                    keyword=f"{line_name}客户案例",
                    kind="长尾词",
                    intent="信任建立",
                    priority="B",
                    business_line=line_name,
                    customer_type=customer_type,
                    search_stage="决策",
                )

            for direction in keywords_direction:
                self._add_keyword(
                    keywords,
                    seen,
                    keyword=direction,
                    kind="业务词",
                    intent="方案咨询",
                    priority="B",
                    business_line=line_name,
                    customer_type=customer_type,
                    search_stage="需求",
                )

        grouped = {
            "品牌词": [k for k in keywords if k["type"] == "品牌词"],
            "业务词": [k for k in keywords if k["type"] == "业务词"],
            "问答词": [k for k in keywords if k["type"] == "问答词"],
            "场景词": [k for k in keywords if k["type"] == "场景词"],
            "长尾词": [k for k in keywords if k["type"] == "长尾词"],
        }
        file_path = write_xlsx(
            output_dir / "keyword_matrix.xlsx",
            "GEO关键词矩阵",
            ["关键词", "类型", "意图", "优先级", "业务线", "客户类型", "搜索阶段"],
            [
                (
                    k["keyword"],
                    k["type"],
                    k["intent"],
                    k["priority"],
                    k["business_line"],
                    k["customer_type"],
                    k["search_stage"],
                )
                for k in keywords
            ],
        )

        return {
            "task": self.task,
            "status": "success",
            "result": {
                "keywords": keywords,
                "grouped": grouped,
                "files": [str(file_path)],
            },
            "next_action": "persona_analysis",
        }

    def _add_keyword(
        self,
        keywords: List[Dict[str, str]],
        seen: set,
        keyword: str,
        kind: str,
        intent: str,
        priority: str,
        business_line: str,
        customer_type: str,
        search_stage: str,
    ) -> None:
        if not keyword:
            return
        key = (keyword, business_line)
        if key in seen:
            return
        seen.add(key)
        keywords.append(
            {
                "keyword": keyword,
                "type": kind,
                "intent": intent,
                "priority": priority,
                "business_line": business_line,
                "customer_type": customer_type,
                "search_stage": search_stage,
            }
        )

    def _brand_words(self, name: str, short_name: str, industry: str) -> List[tuple]:
        return [
            (name, "品牌认知", "A"),
            (short_name, "品牌认知", "A"),
            (f"{short_name} {industry}", "品牌检索", "A"),
        ]
