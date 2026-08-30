"""Deterministic knowledge extractor for local GEO runs."""

from __future__ import annotations

import re
from typing import Any, Dict, List


class KnowledgeExtractor:
    SECTION_HEADING = re.compile(r"^[一二三四五六七八九十]+、\s*(.+?)[:：]?$")
    NUMBERED_ITEM = re.compile(r"^\d+[.、]\s*(.+)$")
    INDUSTRY_RULES = [
        (("装修", "装饰", "整装", "家装"), "建筑装饰装修"),
        (("瓷砖", "陶瓷", "卫浴"), "瓷砖建材"),
        (
            ("工业自动化", "自动化设备", "包装设备", "开箱机", "包装生产线"),
            "工业自动化设备",
        ),
        (("软件", "SaaS", "人工智能"), "企业软件服务"),
        (("物流", "仓储", "供应链"), "物流仓储"),
        (("食品", "饮料"), "食品加工"),
        (("医疗", "医药"), "医疗健康"),
        (("教育", "培训"), "教育培训"),
        (("电商", "零售"), "电商零售"),
    ]

    def extract(
        self,
        content: str,
        chunks: List[Dict[str, Any]] | None = None,
    ) -> Dict[str, Any]:
        content = content or ""
        company = {
            "company_name": self._company_name(content),
            "website": self._first_value(content, ["官网", "官网地址", "网址", "website"]),
            "industry": self._industry(content),
            "services": self._dedupe(
                self._values(content, ["服务", "服务内容"])
                + self._section_items(content, ["全流程服务体系"])
            ),
            "customers": self._dedupe(
                self._values(content, ["客户", "目标客户", "客户群体"])
                + self._infer_customers(content)
            ),
        }
        products = self._products(content)
        market = {
            "pain_points": self._dedupe(
                self._values(content, ["痛点", "客户痛点"])
                + self._infer_pain_points(content)
            ),
            "search_needs": self._search_needs(content, chunks),
            "ai_questions": self._ai_questions(content, chunks),
        }
        return {
            "company": company,
            "products": products,
            "market": market,
        }

    @staticmethod
    def _company_name(content: str) -> str:
        direct = KnowledgeExtractor._first_value(content, ["公司名称", "企业名称", "公司"])
        if direct:
            return direct
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            match = re.match(r"^(.+?)(?:企业介绍|企业简介|公司介绍|公司简介)", stripped)
            if match:
                return match.group(1).strip()
            if (
                len(stripped) <= 80
                and re.search(r"(公司|中心|工厂|厂|店|商行|超市)$", stripped)
            ):
                return stripped
        return ""

    @staticmethod
    def _industry(content: str) -> str:
        direct = KnowledgeExtractor._first_value(content, ["行业", "所属行业"])
        if direct:
            return direct
        for keywords, industry in KnowledgeExtractor.INDUSTRY_RULES:
            if any(keyword in content for keyword in keywords):
                return industry
        return ""

    @staticmethod
    def _section_items(
        content: str,
        headings: List[str],
        max_items: int = 20,
    ) -> List[str]:
        items: List[str] = []
        active = False
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            heading_match = KnowledgeExtractor.SECTION_HEADING.match(stripped)
            if heading_match:
                title = heading_match.group(1).strip()
                if any(heading in title for heading in headings):
                    active = True
                    continue
                if active:
                    active = False
            if not active:
                continue
            item_match = KnowledgeExtractor.NUMBERED_ITEM.match(stripped)
            if item_match:
                item = KnowledgeExtractor._clean_item(item_match.group(1))
                if item and item not in items:
                    items.append(item)
                    if len(items) >= max_items:
                        break
        return items

    @staticmethod
    def _clean_item(item: str) -> str:
        cleaned = re.sub(r"^[-–—•·]\s*", "", item).strip()
        cleaned = re.sub(
            r"\s*[（(](?:室内全空间系列|外立面全系列|全系列|系列)[）)]$",
            "",
            cleaned,
        )
        return cleaned.strip()

    @staticmethod
    def _first_value(content: str, labels: List[str]) -> str:
        for label in labels:
            matches = re.findall(
                rf"(?:^|[\n：:，,。；;])\s*{re.escape(label)}\s*[:：]\s*([^\n]+)",
                content,
                flags=re.MULTILINE,
            )
            if matches and matches[0].strip():
                return matches[0].strip()
        return ""

    @staticmethod
    def _dedupe(items: List[str]) -> List[str]:
        seen: List[str] = []
        for item in items:
            if item and item not in seen:
                seen.append(item)
        return seen

    @staticmethod
    def _values(content: str, labels: List[str]) -> List[str]:
        values = []
        for label in labels:
            matches = re.findall(
                rf"(?:^|[\n：:，,。；;])\s*{re.escape(label)}\s*[:：]\s*([^\n]+)",
                content,
                flags=re.MULTILINE,
            )
            for match in matches:
                for item in re.split(r"[、,，;；/|\n]+", match.strip()):
                    if item and item not in values:
                        values.append(item.strip())
        return values

    @staticmethod
    def _products(content: str) -> List[Dict[str, str]]:
        raw_products = KnowledgeExtractor._values(content, ["产品", "主营产品"])
        for item in KnowledgeExtractor._section_items(
            content,
            ["产品体系", "产品与服务体系", "产品与服务"],
        ):
            if item not in raw_products:
                raw_products.append(item)
        products = []
        for item in raw_products:
            product = {"product_name": item}
            if "开箱" in item:
                product["advantages"] = ["自动化开箱", "降低人工依赖", "支持定制"]
                product["application_scenarios"] = ["食品产线", "物流分拣", "制造包装"]
            elif "包装" in item:
                product["advantages"] = ["包装效率高", "规格切换灵活", "质量稳定"]
                product["application_scenarios"] = ["食品包装", "日化包装", "工业品包装"]
            elif "瓷砖" in item or "陶瓷" in item:
                product["advantages"] = ["品牌正品直供", "仓储现货充足", "支持全案服务"]
                product["application_scenarios"] = ["家装自住", "别墅自建房", "工程集采"]
            elif "装修" in item or "装饰" in item:
                product["advantages"] = ["官方品牌授权", "透明报价", "直管施工交付"]
                product["application_scenarios"] = ["家装整装", "公装工程", "旧房翻新"]
            else:
                product["advantages"] = []
                product["application_scenarios"] = []
            products.append(product)
        return products

    @staticmethod
    def _infer_customers(content: str) -> List[str]:
        rules = [
            ("家庭客户", "家庭客户"),
            ("商业客户", "商业客户"),
            ("装修公司", "装修公司"),
            ("工程方", "工程客户"),
            ("业主", "家装业主"),
            ("食品企业", "食品企业"),
            ("物流企业", "物流企业"),
            ("制造企业", "制造企业"),
        ]
        customers = []
        for keyword, label in rules:
            if keyword in content and label not in customers:
                customers.append(label)
        return customers[:6]

    @staticmethod
    def _infer_pain_points(content: str) -> List[str]:
        rules = [
            ("质量", "质量与售后保障"),
            ("工期", "交付工期不确定性"),
            ("价格", "价格与成本不透明"),
            ("效率低", "运营效率低"),
            ("人工成本", "人工成本高"),
            ("定制", "定制化需求响应慢"),
            ("环保", "环保合规要求"),
        ]
        pain_points = []
        for keyword, label in rules:
            if keyword in content and label not in pain_points:
                pain_points.append(label)
        return pain_points[:6]

    @staticmethod
    def _search_needs(
        content: str,
        chunks: List[Dict[str, Any]] | None,
    ) -> List[str]:
        needs = KnowledgeExtractor._values(
            content,
            ["搜索需求", "用户搜索", "采购搜索"],
        )
        if not needs and chunks:
            keywords = ("厂家", "报价", "定制", "解决方案", "案例", "价格")
            for chunk in chunks:
                for keyword in keywords:
                    if keyword in chunk.get("text", ""):
                        candidate = f"了解{keyword}相关信息"
                        if candidate not in needs:
                            needs.append(candidate)
        if not needs:
            needs = ["了解企业产品与解决方案", "获取厂家资质与案例"]
        return needs

    @staticmethod
    def _ai_questions(
        content: str,
        chunks: List[Dict[str, Any]] | None,
    ) -> List[str]:
        questions = KnowledgeExtractor._values(
            content,
            ["AI问答", "AI问题", "问答问题"],
        )
        if not questions and chunks:
            product_names = []
            for chunk in chunks:
                text = chunk.get("text", "")
                match = re.search(r"(自动开箱机|自动包装设备|自动化包装生产线|包装设备|开箱机)", text)
                if match and match.group(1) not in product_names:
                    product_names.append(match.group(1))
            for product in product_names[:3]:
                questions.append(f"{product}厂家有哪些")
                questions.append(f"{product}定制方案和价格")
                questions.append(f"{product}应用案例")
        if not questions:
            questions = ["工业自动化包装设备如何选型", "自动化开箱机厂家有哪些"]
        return questions
