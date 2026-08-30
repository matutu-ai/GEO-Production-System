"""GEO service layer: task registry and pipeline execution."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from workflow.pipeline import GEOPipeline

BASE_DIR = Path(__file__).resolve().parents[1]
STORAGE_DIR = BASE_DIR / "storage"
UPLOAD_DIR = STORAGE_DIR / "uploads"
TASK_OUTPUT_DIR = BASE_DIR / "output" / "tasks"


@dataclass
class GEOJob:
    task_id: str
    status: str = "queued"
    source_file: str = ""
    output_dir: str = ""
    output_files: List[str] = field(default_factory=list)
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "status": self.status,
            "source_file": self.source_file,
            "output_dir": self.output_dir,
            "output_files": self.output_files,
            "message": self.message,
        }


class GeoService:
    """In-memory job runner for the local GEO pipeline."""

    def __init__(self) -> None:
        self.jobs: Dict[str, GEOJob] = {}

    def run_analysis(
        self,
        source_file: Path,
        task_id: Optional[str] = None,
    ) -> GEOJob:
        current_id = task_id or uuid.uuid4().hex[:12]
        output_dir = TASK_OUTPUT_DIR / current_id
        job = GEOJob(
            task_id=current_id,
            status="running",
            source_file=str(source_file),
            output_dir=str(output_dir),
        )
        self.jobs[current_id] = job

        try:
            result = GEOPipeline(output_dir=str(output_dir)).run(
                input_path=str(source_file)
            )
        except Exception as exc:
            job.status = "error"
            job.message = str(exc)
            return job

        if result.get("status") != "success":
            job.status = "error"
            job.message = result.get("message", "GEO pipeline failed")
            return job

        job.status = "success"
        job.output_files = result.get("result", {}).get("files", [])
        return job

    def get_job(self, task_id: str) -> Optional[GEOJob]:
        return self.jobs.get(task_id)
