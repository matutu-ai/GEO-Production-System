"""Business Agent: company profile -> business line decomposition."""

from __future__ import annotations

from typing import Any, Dict, List


class BusinessAgent:
    task = "business_analysis"

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        profile = input_data.get("result", input_data)
        products = profile.get("products", [])
        services = profile.get("services", [])
        industry = profile.get("industry", "")

        if not products and not services:
            return self._error("products or services are required")

        seed_items = list(products)
        if len(seed_items) < 3:
            for service in services:
                if service not in seed_items:
                    seed_items.append(service)
        if len(seed_items) < 3 and industry:
            seed_items.append(f"{industry}整体解决方案")

        business_lines = [
            self._build_line(profile, item, index)
            for index, item in enumerate(seed_items[:3])
        ]
        return {
            "task": self.task,
            "status": "success",
            "confidence": self._confidence(business_lines),
            "result": {"business_lines": business_lines},
            "next_action": "keyword_analysis",
        }

    def _build_line(
        self,
        profile: Dict[str, Any],
        business_item: str,
        index: int,
    ) -> Dict[str, Any]:
        industry = profile.get("industry", "工业自动化")
        customers = profile.get("target_customers") or [f"{industry}下游客户"]
        problems = self._problems(business_item, index)
        buying_intent = [
            f"采购{business_item}",
            f"{business_item}厂家",
            f"{business_item}报价",
            f"{business_item}供应商",
        ]
        keywords_direction = [
            business_item,
            f"{business_item}厂家",
            f"{business_item}解决方案",
            f"{business_item}定制",
            f"{business_item}案例",
        ]
        content_direction = [
            f"{business_item}选型指南",
            f"{business_item}实施案例",
            f"{business_item}常见问题",
        ]
        return {
            "business_name": f"{business_item}解决方案",
            "products": [business_item],
            "target_customers": customers,
            "customer_problems": problems,
            "buying_intent": buying_intent,
            "keywords_direction": keywords_direction,
            "content_direction": content_direction,
        }

    def _problems(self, business_item: str, index: int) -> List[str]:
        if "开箱" in business_item:
            return [
                "人工开箱效率低",
                "开箱破损率偏高",
                "开箱环节与产线衔接不顺畅",
            ]
        if "包装" in business_item and "生产" not in business_item:
            return [
                "人工包装成本高",
                "包装规格切换慢",
                "包装质量一致性不足",
            ]
        if "生产线" in business_item or "整体" in business_item:
            return [
                "整线自动化程度不足",
                "多设备协同困难",
                "产线升级周期长",
            ]
        return [
            f"{business_item}落地经验不足",
            "设备与现有产线兼容性风险",
            "定制需求响应周期长",
        ]

    def _confidence(self, business_lines: List[Dict[str, Any]]) -> int:
        score = 70
        if len(business_lines) >= 3:
            score += 20
        if business_lines and all(line.get("products") for line in business_lines):
            score += 10
        return min(100, score)

    def _error(self, message: str) -> Dict[str, Any]:
        return {
            "task": self.task,
            "status": "error",
            "confidence": 0,
            "result": {"business_lines": []},
            "next_action": "fix_company_profile",
            "message": message,
        }
