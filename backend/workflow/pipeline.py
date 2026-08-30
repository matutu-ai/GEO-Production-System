"""GEO Production Tool pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, Optional

from agents.business_agent import BusinessAgent
from agents.company_agent import CompanyAgent
from agents.content_agent import ContentAgent
from agents.input_parser_agent import InputParserAgent
from agents.keyword_agent import KeywordAgent
from agents.monitor_agent import MonitorAgent
from agents.persona_agent import PersonaAgent
from agents.report_agent import ReportAgent
from agents.score_agent import ScoreAgent
from agents.strategy_agent import StrategyAgent
from file_writer import save_json

BASE_DIR = Path(__file__).resolve().parents[1]


class GEOPipeline:
    def __init__(self, output_dir: Optional[str] = None) -> None:
        self.output_dir = Path(output_dir or BASE_DIR / "output")

    def run(
        self,
        customer_data: Optional[Dict[str, Any]] = None,
        input_path: Optional[str] = None,
        status_callback: Optional[Callable[[str], None]] = None,
    ) -> Dict[str, Any]:
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if input_path:
            if status_callback:
                status_callback("PARSING")
            parsed = InputParserAgent().run(str(input_path))
            if parsed.get("status") != "success":
                return parsed
            standardized = parsed["result"]
            save_json(self.output_dir / "customer_profile.json", standardized)
        elif customer_data:
            standardized = dict(customer_data)
            save_json(self.output_dir / "customer_profile.json", standardized)
        else:
            return self._error("customer_data or input_path is required")

        if status_callback:
            status_callback("ANALYZING")

        company_input = dict(standardized)
        company_input["output_dir"] = str(self.output_dir)
        company_result = CompanyAgent().run(company_input)
        save_json(self.output_dir / "company_profile.json", company_result)
        if company_result.get("status") != "success":
            return company_result

        business_input = dict(company_result)
        business_input["output_dir"] = str(self.output_dir)
        business_result = BusinessAgent().run(business_input)
        save_json(
            self.output_dir / "business_analysis.json",
            business_result.get("result", {}),
        )
        if business_result.get("status") != "success":
            return business_result

        keyword_input = {
            "company_profile": company_result["result"],
            "business_analysis": business_result["result"],
            "output_dir": str(self.output_dir),
        }
        keyword_result = KeywordAgent().run(keyword_input)
        save_json(self.output_dir / "keywords.json", keyword_result)

        persona_result = PersonaAgent().run(
            {
                "result": company_result["result"],
                "output_dir": str(self.output_dir),
            }
        )
        save_json(self.output_dir / "personas.json", persona_result)

        content_input = {
            "company_profile": company_result["result"],
            "keyword_result": keyword_result,
            "persona_result": persona_result,
            "output_dir": str(self.output_dir),
        }
        content_result = ContentAgent().run(content_input)
        save_json(self.output_dir / "content_plan.json", content_result)

        strategy_input = {
            "company_profile": company_result["result"],
            "business_analysis": business_result["result"],
            "keyword_result": keyword_result,
            "persona_result": persona_result,
            "content_result": content_result,
            "output_dir": str(self.output_dir),
        }
        strategy_result = StrategyAgent().run(strategy_input)
        if strategy_result.get("status") != "success":
            return strategy_result

        monitor_result = MonitorAgent().run(
            {
                "customer_name": standardized.get("name", ""),
                "company_profile": company_result,
                "keyword_result": keyword_result,
                "persona_result": persona_result,
                "content_result": content_result,
                "strategy_result": strategy_result,
            }
        )
        save_json(self.output_dir / "monitor_report.json", monitor_result)

        score_result = ScoreAgent().run(
            {
                "company_profile": company_result,
                "keyword_result": keyword_result,
                "persona_result": persona_result,
                "content_result": content_result,
                "monitor_result": monitor_result,
            }
        )
        save_json(self.output_dir / "geo_score.json", score_result)

        if status_callback:
            status_callback("GENERATING")

        report_result = ReportAgent().run(
            {
                "customer_data": standardized,
                "company_profile": company_result["result"],
                "business_result": business_result,
                "keyword_result": keyword_result,
                "persona_result": persona_result,
                "content_result": content_result,
                "strategy_result": strategy_result,
                "monitor_result": monitor_result,
                "score_result": score_result,
                "output_dir": str(self.output_dir),
            }
        )
        report_result["result"]["files"] = self._collect_files(
            report_result,
            company_result,
            business_result,
            keyword_result,
            persona_result,
            content_result,
            strategy_result,
            monitor_result,
            score_result,
        )
        save_json(self.output_dir / "pipeline_result.json", report_result)
        return report_result

    def _collect_files(
        self,
        report_result: Dict[str, Any],
        company_result: Dict[str, Any],
        business_result: Dict[str, Any],
        keyword_result: Dict[str, Any],
        persona_result: Dict[str, Any],
        content_result: Dict[str, Any],
        strategy_result: Dict[str, Any],
        monitor_result: Dict[str, Any],
        score_result: Dict[str, Any],
    ) -> list:
        files = []
        for result_item in (
            company_result,
            business_result,
            keyword_result,
            persona_result,
            content_result,
            strategy_result,
            monitor_result,
            score_result,
            report_result,
        ):
            files.extend(result_item.get("result", {}).get("files", []))
        files.append(str(self.output_dir / "customer_profile.json"))
        files.append(str(self.output_dir / "business_analysis.json"))
        files.append(str(self.output_dir / "strategy_plan.json"))
        files.append(str(self.output_dir / "monitor_report.json"))
        files.append(str(self.output_dir / "geo_score.json"))
        unique = []
        for file_path in files:
            if file_path not in unique:
                unique.append(file_path)
        return unique

    def _error(self, message: str) -> Dict[str, Any]:
        return {
            "task": "geo_pipeline",
            "status": "error",
            "confidence": 0,
            "result": {"files": []},
            "next_action": "fix_input",
            "message": message,
        }
