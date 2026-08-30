"""Company Agent: enterprise input -> GEO company profile."""

from __future__ import annotations

import re
from typing import Any, Dict, List


class CompanyAgent:
    task = "company_analysis"

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        knowledge_result = self._knowledge_result(input_data)
        knowledge = self._knowledge(input_data)
        name = (
            self._clean(input_data.get("name") or input_data.get("company_name"))
            or self._clean(knowledge.get("company_name"))
        )
        website = self._clean(input_data.get("website")) or self._clean(
            knowledge.get("website")
        )
        industry = self._clean(input_data.get("industry")) or self._clean(
            knowledge.get("industry")
        )
        products = self._split(input_data.get("products")) or self._knowledge_products(
            knowledge_result
        )
        services = self._split(input_data.get("services")) or self._split(
            knowledge.get("services")
        )
        advantages = self._split(input_data.get("advantages"))
        cases = self._split(input_data.get("cases"))
        knowledge_customers = self._split(knowledge.get("customers"))

        if not name or not industry or not products:
            return self._error("name, industry and products are required")

        positioning = f"{name}专注于{industry}领域，主营{self._join(products)}"
        if services:
            positioning += f"，并提供{self._join(services)}"

        result = {
            "company_name": name,
            "company_positioning": positioning,
            "industry": industry,
            "products": products,
            "services": services,
            "target_customers": self._build_customers(
                industry, cases, knowledge_customers
            ),
            "advantages": advantages,
            "customer_pain_points": self._build_pain_points(industry),
            "evidence": self._build_evidence(website, cases),
        }
        return {
            "task": self.task,
            "status": "success",
            "confidence": self._confidence(result),
            "result": result,
            "next_action": "keyword_analysis",
        }

    def _clean(self, value: Any) -> str:
        return "" if value is None else str(value).strip()

    @staticmethod
    def _knowledge(input_data: Dict[str, Any]) -> Dict[str, Any]:
        result = CompanyAgent._knowledge_result(input_data)
        base = result.get("knowledge_base", result)
        return base.get("company", base) if isinstance(base, dict) else {}

    @staticmethod
    def _knowledge_result(input_data: Dict[str, Any]) -> Dict[str, Any]:
        raw = input_data.get("knowledge_extract") or {}
        result = raw.get("result", raw) if isinstance(raw, dict) else {}
        return result if isinstance(result, dict) else {}

    @staticmethod
    def _knowledge_products(knowledge_result: Dict[str, Any]) -> List[str]:
        products = []
        for item in knowledge_result.get("products", []):
            if isinstance(item, str):
                products.append(item)
            elif isinstance(item, dict) and item.get("product_name"):
                products.append(item["product_name"])
        return products

    def _split(self, value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [self._clean(item) for item in value if self._clean(item)]
        parts = re.split(r"[、,，;；/|\n]+", self._clean(value))
        return [part.strip() for part in parts if part.strip()]

    def _join(self, items: List[str]) -> str:
        return "、".join(items)

    def _build_customers(
        self,
        industry: str,
        cases: List[str],
        knowledge_customers: List[str],
    ) -> List[str]:
        customers: List[str] = list(knowledge_customers)
        for case in cases:
            for item in self._split(case):
                if item not in customers:
                    customers.append(item)
        if not customers:
            customers.append(f"{industry}下游客户")
        return customers

    def _build_pain_points(self, industry: str) -> List[str]:
        if industry == "工业自动化设备":
            return ["产线效率低", "人工成本高", "设备兼容性差", "定制需求响应慢"]
        return ["自动化升级需求", "交付周期要求高", "定制化服务需求"]

    def _build_evidence(self, website: str, cases: List[str]) -> List[str]:
        evidence = []
        if website:
            evidence.append(f"官网：{website}")
        if cases:
            evidence.append(f"客户案例：{'、'.join(cases)}")
        return evidence

    def _confidence(self, result: Dict[str, Any]) -> int:
        score = 70
        if result.get("company_positioning"):
            score += 10
        if result.get("target_customers"):
            score += 10
        if result.get("evidence"):
            score += 10
        return min(100, score)

    def _error(self, message: str) -> Dict[str, Any]:
        return {
            "task": self.task,
            "status": "error",
            "confidence": 0,
            "result": {
                "company_name": "",
                "company_positioning": "",
                "industry": "",
                "products": [],
                "services": [],
                "target_customers": [],
                "advantages": [],
                "customer_pain_points": [],
                "evidence": [],
            },
            "next_action": "fix_input",
            "message": message,
        }
