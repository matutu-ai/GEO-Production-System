"""Service layer for the isolated GEO Analysis module."""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

from config.settings import STORAGE_PATH
from geo_analysis_loader import get_geo_module

LOGGER = logging.getLogger(__name__)

Store = get_geo_module("storage")
Pipeline = get_geo_module("workflow.geo_pipeline")


class GeoAnalysisService:
    """Create and run GEO Analysis projects without touching existing pipelines."""

    def __init__(self) -> None:
        store_path = STORAGE_PATH / "geo_analysis" / "projects.json"
        self.store = Store.get_geo_project_store(store_path)
        self.output_dir = STORAGE_PATH / "geo_analysis" / "exports"

    def create_project(self, name: str, source: str = "") -> Dict[str, Any]:
        project = self.store.create(name=name, source=source)
        return project.model_dump()

    def start_analysis(
        self,
        project_id: str,
        input_data: Dict[str, Any],
        sync: bool = False,
    ) -> Dict[str, Any]:
        project = self.store.get(project_id)
        if not project:
            raise ValueError("project not found")
        self.store.update(project_id, status="PROCESSING", progress=5)
        if sync:
            self._run(project_id, input_data)
        else:
            thread = threading.Thread(
                target=self._run,
                args=(project_id, input_data),
                daemon=True,
            )
            thread.start()
        current = self.store.get(project_id)
        return current.model_dump() if current else {}

    def _run(self, project_id: str, input_data: Dict[str, Any]) -> None:
        try:
            pipeline_class = Pipeline.GEOAnalysisPipeline
            pipeline = pipeline_class(output_dir=self.output_dir)

            def progress(stage: str, progress: int):
                self.store.update(project_id, status=stage, progress=progress)

            output = pipeline.run(
                project_id=project_id,
                input_data=input_data,
                progress_callback=progress,
            )
            result = output.get("result", {})
            self.store.update(
                project_id,
                status="COMPLETED",
                progress=100,
                analysis_result=result,
                svg_file=output.get("svg_file", ""),
            )
        except Exception as exc:
            LOGGER.exception("GEO analysis project %s failed", project_id)
            self.store.update(
                project_id,
                status="FAILED",
                progress=100,
                analysis_result={"error": str(exc)},
            )

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        project = self.store.get(project_id)
        return project.model_dump() if project else None

    def list_projects(self) -> List[Dict[str, Any]]:
        return [project.model_dump() for project in self.store.list()]

    def list_exports(self, project_id: str) -> List[Dict[str, Any]]:
        project_dir = self.output_dir / project_id
        if not project_dir.is_dir():
            return []
        files = []
        for path in sorted(project_dir.iterdir()):
            if path.is_file() and path.stat().st_size > 0:
                files.append(
                    {
                        "filename": path.name,
                        "path": str(path),
                        "size": path.stat().st_size,
                        "content_type": self._content_type(path.name),
                    }
                )
        return files

    def get_export_path(self, project_id: str, filename: str) -> Optional[Path]:
        allowed = {item["filename"] for item in self.list_exports(project_id)}
        if filename not in allowed:
            return None
        return self.output_dir / project_id / filename

    @staticmethod
    def _content_type(filename: str) -> str:
        mapping = {
            ".json": "application/json",
            ".md": "text/markdown",
            ".html": "text/html",
            ".pdf": "application/pdf",
            ".svg": "image/svg+xml",
            ".png": "image/png",
        }
        suffix = Path(filename).suffix.lower()
        return mapping.get(suffix, "application/octet-stream")
