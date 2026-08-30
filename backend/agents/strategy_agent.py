"""Strategy Agent: analysis results -> executable GEO optimization plan."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from file_writer import save_json

BASE_DIR = Path(__file__).resolve().parents[1]


class StrategyAgent:
    task = "strategy_generation"

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        company = input_data.get("company_profile", {}) or {}
        business = input_data.get("business_analysis", {}) or {}
        if isinstance(business, dict) and "result" in business:
            business = business.get("result", {})
        keyword_result = self._result(input_data, "keyword_result", "keyword_matrix")
        persona_result = self._result(input_data, "persona_result", "persona_report")
        content_result = self._result(input_data, "content_result", "content_plan")
        output_dir = Path(input_data.get("output_dir", BASE_DIR / "output"))

        business_lines = business.get("business_lines", [])
        keywords = keyword_result.get("keywords", [])
        personas = persona_result.get("personas", [])
        content_plan = content_result.get("plan", [])

        priority_actions = (
            self._p1_actions(company, keywords, personas, business_lines)
            + self._p2_actions(company, keywords, personas, content_plan)
            + self._p3_actions(company, business_lines)
        )
        summary = (
            f"围绕{company.get('company_name', '客户')}的"
            f"{len(business_lines)}条业务线，先补齐品牌、问答和案例三类GEO基础，"
            "再通过30天内容计划持续扩大AI搜索中的可见度。"
        )
        result = {
            "summary": summary,
            "priority_actions": priority_actions,
            "30_day_plan": self._build_weeks(content_plan, business_lines),
        }
        save_json(output_dir / "strategy_plan.json", result)
        return {
            "task": self.task,
            "status": "success",
            "confidence": self._confidence(result),
            "result": result,
            "next_action": "report_generation",
        }

    def _result(
        self,
        input_data: Dict[str, Any],
        primary_key: str,
        fallback_key: str,
    ) -> Dict[str, Any]:
        item = input_data.get(primary_key) or input_data.get(fallback_key) or {}
        if isinstance(item, dict) and "result" in item:
            return item.get("result", {})
        return item

    def _p1_actions(
        self,
        company: Dict[str, Any],
        keywords: List[Dict[str, Any]],
        personas: List[Dict[str, Any]],
        business_lines: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        brand = self._keywords(keywords, ["品牌词"])
        business_words = self._keywords(keywords, ["业务词"])
        qa = self._keywords(keywords, ["问答词"])
        case = self._keywords(keywords, ["场景词", "长尾词"])
        return [
            {
                "priority": "P1",
                "action": "官网首页与产品页补齐企业定位、产品卖点和案例证据",
                "reason": "品牌词和业务词决定AI回答中第一轮品牌曝光",
                "related_keywords": brand[:4] + business_words[:3],
                "target_users": self._target_users(personas, ["老板", "采购负责人"]),
                "content_needed": "企业定位文案、产品介绍、客户证据页",
                "expected_value": "提高品牌词和核心业务词被AI推荐的概率",
            },
            {
                "priority": "P1",
                "action": "建设FAQ与结构化问答内容",
                "reason": "采购和选型阶段常以问答方式检索，结构化内容更容易被引用",
                "related_keywords": qa[:6],
                "target_users": self._target_users(personas, ["采购负责人", "技术负责人"]),
                "content_needed": "FAQ页面、问答结构化数据、价格与选型说明",
                "expected_value": "覆盖采购决策期的AI问答检索",
            },
            {
                "priority": "P1",
                "action": "发布3条业务线客户案例",
                "reason": "场景词和信任类长尾词需要真实案例作为可引用证据",
                "related_keywords": case[:6],
                "target_users": self._target_users(personas, ["老板", "技术负责人"]),
                "content_needed": "食品、物流、制造行业案例内容",
                "expected_value": "增强品牌在方案对比场景中的可信度",
            },
        ]

    def _p2_actions(
        self,
        company: Dict[str, Any],
        keywords: List[Dict[str, Any]],
        personas: List[Dict[str, Any]],
        content_plan: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        scenario = self._keywords(keywords, ["场景词"])
        longtail = self._keywords(keywords, ["长尾词"])
        task_count = max(3, len(content_plan) // 7)
        return [
            {
                "priority": "P2",
                "action": f"为{company.get('company_name', '客户')}的每条业务线建立专题页面",
                "reason": "独立业务专题可以承接不同搜索意图，提升内容相关性",
                "related_keywords": scenario[:5],
                "target_users": self._target_users(personas, ["技术负责人", "采购负责人"]),
                "content_needed": "业务线介绍、技术参数、定制流程、案例入口",
                "expected_value": "让每条业务线都有可被AI抓取的专题页面",
            },
            {
                "priority": "P2",
                "action": f"执行30天内容计划，首批完成{task_count}个核心主题",
                "reason": "持续更新是扩大AI搜索覆盖的基础动作",
                "related_keywords": longtail[:5],
                "target_users": self._target_users(personas, ["采购负责人", "技术负责人"]),
                "content_needed": "30天官网文章、FAQ和案例内容",
                "expected_value": "形成稳定的内容输出和关键词覆盖节奏",
            },
            {
                "priority": "P2",
                "action": "统一官网元信息、品牌资料和第三方平台企业信息",
                "reason": "品牌信息一致性能提高AI对企业的识别置信度",
                "related_keywords": self._keywords(keywords, ["品牌词"])[:4],
                "target_users": self._target_users(personas, ["老板"]),
                "content_needed": "官网Title/Description、公司简介、资质证书",
                "expected_value": "降低品牌信息冲突，增强GEO证据一致性",
            },
        ]

    def _p3_actions(
        self,
        company: Dict[str, Any],
        business_lines: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        return [
            {
                "priority": "P3",
                "action": "建立AI搜索可见度监测与验证机制",
                "reason": "只有持续监测ChatGPT、Claude、Gemini等回答，才能判断GEO策略效果",
                "related_keywords": ["品牌出现率", "竞品出现率", "推荐理由"],
                "target_users": ["项目负责人"],
                "content_needed": "GEO验证问题集、月度监测记录",
                "expected_value": "形成可量化的GEO可见度评分",
            },
            {
                "priority": "P3",
                "action": "持续沉淀行业研究、竞品对比和长尾内容",
                "reason": "AI搜索更倾向于引用有数据、有对比、有行业深度的内容",
                "related_keywords": self._keywords_from_lines(business_lines),
                "target_users": ["技术负责人", "行业客户"],
                "content_needed": "行业趋势、竞品对比、技术白皮书",
                "expected_value": "扩大非品牌词的长期搜索覆盖",
            },
            {
                "priority": "P3",
                "action": "把客户成功数据转化为可引用的GEO证据",
                "reason": "真实效率、案例数据比营销语言更可能被AI引用",
                "related_keywords": ["客户案例数据", "自动化效率提升", "设备交期案例"],
                "target_users": ["老板", "采购负责人"],
                "content_needed": "客户证言、效率数据、现场图片与视频",
                "expected_value": "建立长期差异化品牌证据池",
            },
        ]

    def _build_weeks(
        self,
        content_plan: List[Dict[str, Any]],
        business_lines: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        business_names = [line.get("business_name", "") for line in business_lines]
        weeks = [
            {
                "week": "第1周",
                "tasks": [
                    "发布企业定位与核心产品页内容",
                    "完成FAQ问题清单并上线结构化问答",
                    "启动3条业务线案例内容框架",
                ],
            },
            {
                "week": "第2周",
                "tasks": [
                    "发布业务词选型指南和厂家对比内容",
                    "补齐关键词矩阵中的A级高价值主题",
                    "统一官网元信息与品牌资料",
                ],
            },
            {
                "week": "第3周",
                "tasks": [
                    "发布食品、物流、制造行业场景案例",
                    "围绕采购和技术画像输出决策型内容",
                    "同步第三方行业平台与官网内容",
                ],
            },
            {
                "week": "第4周",
                "tasks": [
                    "完成30天内容计划第一轮复盘",
                    "建立AI搜索可见度验证问题集",
                    "输出下一周期关键词与内容优化清单",
                ],
            },
        ]
        if content_plan:
            for index, week in enumerate(weeks):
                start = index * 7
                for item in content_plan[start : start + 2]:
                    week["tasks"].append(
                        f"按计划发布：{item.get('内容主题', '')}"
                    )
        if business_names:
            for index, week in enumerate(weeks):
                if index < len(business_names):
                    week["tasks"].append(
                        f"完成{business_names[index]}专题页内容骨架"
                    )
        return weeks

    def _keywords(
        self,
        keywords: List[Dict[str, Any]],
        kinds: List[str],
    ) -> List[str]:
        return [
            item.get("keyword", "")
            for item in keywords
            if item.get("type") in kinds and item.get("keyword")
        ]

    def _keywords_from_lines(self, business_lines: List[Dict[str, Any]]) -> List[str]:
        keywords = []
        for line in business_lines:
            keywords.extend(line.get("keywords_direction", [])[:2])
        return keywords[:6]

    def _target_users(
        self,
        personas: List[Dict[str, Any]],
        role_names: List[str],
    ) -> List[str]:
        users = []
        for persona in personas:
            role = persona.get("role", "")
            if role in role_names and role not in users:
                users.append(role)
        if not users:
            users = ["目标客户"]
        return users

    def _confidence(self, result: Dict[str, Any]) -> int:
        actions = result.get("priority_actions", [])
        p1 = sum(1 for action in actions if action.get("priority") == "P1")
        p2 = sum(1 for action in actions if action.get("priority") == "P2")
        p3 = sum(1 for action in actions if action.get("priority") == "P3")
        score = 70
        if p1 >= 3:
            score += 10
        if p2 >= 3:
            score += 10
        if p3 >= 3:
            score += 10
        return min(100, score)
