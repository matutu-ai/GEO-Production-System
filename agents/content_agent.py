"""Content Agent: keywords + personas -> 30-day content plan."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from file_writer import write_xlsx

BASE_DIR = Path(__file__).resolve().parents[1]


class ContentAgent:
    task = "content_planning"

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        company_profile = input_data.get("company_profile", {})
        keyword_result = input_data.get("keyword_result", {}).get("result", {})
        persona_result = input_data.get("persona_result", {}).get("result", {})
        output_dir = Path(input_data.get("output_dir", BASE_DIR / "output"))

        keywords = keyword_result.get("keywords", [])
        personas = persona_result.get("personas", [])
        roles = [p.get("role", "目标用户") for p in personas]

        directions = self._content_directions(company_profile, keywords, roles)
        faq_list = self._faq_list(keywords)
        case_list = self._case_list(keywords)
        plan = self._build_plan(directions)

        file_path = write_xlsx(
            output_dir / "content_plan.xlsx",
            "30天内容计划",
            ["日期", "内容主题", "目标关键词", "目标用户", "发布建议"],
            [
                (
                    item["日期"],
                    item["内容主题"],
                    item["目标关键词"],
                    item["目标用户"],
                    item["发布建议"],
                )
                for item in plan
            ],
        )

        return {
            "task": self.task,
            "status": "success",
            "result": {
                "content_directions": directions,
                "faq_list": faq_list,
                "case_list": case_list,
                "plan": plan,
                "files": [str(file_path)],
            },
            "next_action": "report_generation",
        }

    def _content_directions(
        self,
        profile: Dict[str, Any],
        keywords: List[Dict[str, Any]],
        roles: List[str],
    ) -> List[Dict[str, str]]:
        keyword = self._first_keyword(keywords, "业务词")
        qa_keyword = self._first_keyword(keywords, "问答词")
        case_keyword = self._first_keyword(keywords, "场景词")
        longtail_keyword = self._first_keyword(keywords, "长尾词")
        user = roles[0] if roles else "目标用户"

        return [
            {
                "direction": "官网文章",
                "content_topic": f"{keyword}选型指南与厂家实力解析",
                "target_keyword": keyword,
                "target_user": user,
                "publish_suggestion": "发布到官网行业文章栏目，并同步AI搜索优化",
            },
            {
                "direction": "官网文章",
                "content_topic": f"{profile.get('industry', '工业自动化')}如何做自动化升级",
                "target_keyword": qa_keyword,
                "target_user": roles[1] if len(roles) > 1 else user,
                "publish_suggestion": "官网方案中心重点展示",
            },
            {
                "direction": "FAQ",
                "content_topic": f"{qa_keyword}？",
                "target_keyword": qa_keyword,
                "target_user": roles[1] if len(roles) > 1 else user,
                "publish_suggestion": "官网FAQ页面并形成问答结构化数据",
            },
            {
                "direction": "案例",
                "content_topic": f"食品与物流行业{case_keyword}实施案例",
                "target_keyword": case_keyword,
                "target_user": roles[2] if len(roles) > 2 else user,
                "publish_suggestion": "案例页面加入数据、图片和客户见证",
            },
            {
                "direction": "长尾内容",
                "content_topic": f"{longtail_keyword}服务介绍",
                "target_keyword": longtail_keyword,
                "target_user": roles[3] if len(roles) > 3 else user,
                "publish_suggestion": "官网新闻与第三方行业平台同步发布",
            },
        ]

    def _first_keyword(self, keywords: List[Dict[str, Any]], kind: str) -> str:
        for item in keywords:
            if item.get("type") == kind:
                return item.get("keyword", "")
        return keywords[0]["keyword"] if keywords else "工业自动化设备"

    def _faq_list(self, keywords: List[Dict[str, Any]]) -> List[str]:
        return [f"{k['keyword']}？" for k in keywords if k.get("type") == "问答词"][:6]

    def _case_list(self, keywords: List[Dict[str, Any]]) -> List[str]:
        return [f"{k['keyword']}客户案例" for k in keywords if k.get("type") == "场景词"][:6]

    def _build_plan(self, directions: List[Dict[str, str]]) -> List[Dict[str, str]]:
        plan = []
        for day in range(1, 31):
            direction = directions[(day - 1) % len(directions)]
            plan.append(
                {
                    "日期": f"Day {day}",
                    "内容主题": f"第{day}天：{direction['content_topic']}",
                    "目标关键词": direction["target_keyword"],
                    "目标用户": direction["target_user"],
                    "发布建议": direction["publish_suggestion"],
                }
            )
        return plan

