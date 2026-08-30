"""GEO service layer: project registry, background tasks and pipeline execution."""

from __future__ import annotations

import json
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from workflow.pipeline import GEOPipeline

BASE_DIR = Path(__file__).resolve().parents[1]
STORAGE_DIR = BASE_DIR / "storage"
UPLOAD_DIR = STORAGE_DIR / "uploads"
TASK_OUTPUT_DIR = BASE_DIR / "output" / "tasks"
PROJECTS_FILE = STORAGE_DIR / "projects.json"

ANALYSIS_FILES = {
    "customer_profile": "customer_profile.json",
    "company_profile": "company_profile.json",
    "business_analysis": "business_analysis.json",
    "keywords": "keywords.json",
    "personas": "personas.json",
    "content_plan": "content_plan.json",
    "strategy_plan": "strategy_plan.json",
    "pipeline_result": "pipeline_result.json",
}


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


@dataclass
class GEOJob:
    task_id: str
    status: str = "queued"
    customer_name: str = ""
    website: str = ""
    industry: str = ""
    source_file: str = ""
    output_dir: str = ""
    output_files: List[str] = field(default_factory=list)
    message: str = ""
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "status": self.status,
            "customer_name": self.customer_name,
            "website": self.website,
            "industry": self.industry,
            "source_file": self.source_file,
            "output_dir": self.output_dir,
            "output_files": self.output_files,
            "message": self.message,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class GeoService:
    """In-memory project registry persisted to a local JSON file."""

    def __init__(self) -> None:
        self.jobs: Dict[str, GEOJob] = {}
        self._lock = threading.RLock()
        self._load()

    def _load(self) -> None:
        if not PROJECTS_FILE.exists():
            return
        try:
            raw_items = json.loads(PROJECTS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return
        for item in raw_items:
            job = GEOJob(**item)
            self.jobs[job.task_id] = job

    def _save(self) -> None:
        PROJECTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            temp_file = PROJECTS_FILE.with_suffix(".json.tmp")
            payload = [job.to_dict() for job in self.jobs.values()]
            temp_file.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            temp_file.replace(PROJECTS_FILE)

    def start_analysis(
        self,
        source_file: Path,
        task_id: Optional[str] = None,
        customer_name: str = "",
        website: str = "",
        industry: str = "",
    ) -> GEOJob:
        current_id = task_id or uuid.uuid4().hex[:12]
        now = _now_iso()
        job = GEOJob(
            task_id=current_id,
            status="running",
            customer_name=customer_name,
            website=website,
            industry=industry,
            source_file=str(source_file),
            output_dir=str(TASK_OUTPUT_DIR / current_id),
            created_at=now,
            updated_at=now,
        )
        self.jobs[current_id] = job
        self._save()
        thread = threading.Thread(
            target=self._run_async,
            args=(job, Path(source_file)),
            daemon=True,
        )
        thread.start()
        return job

    def run_analysis(
        self,
        source_file: Path,
        task_id: Optional[str] = None,
        customer_name: str = "",
        website: str = "",
        industry: str = "",
    ) -> GEOJob:
        current_id = task_id or uuid.uuid4().hex[:12]
        now = _now_iso()
        job = GEOJob(
            task_id=current_id,
            status="running",
            customer_name=customer_name,
            website=website,
            industry=industry,
            source_file=str(source_file),
            output_dir=str(TASK_OUTPUT_DIR / current_id),
            created_at=now,
            updated_at=now,
        )
        self.jobs[current_id] = job
        self._save()
        self._execute(job, source_file)
        return job

    def _run_async(self, job: GEOJob, source_file: Path) -> None:
        job.status = "running"
        job.updated_at = _now_iso()
        self._save()
        self._execute(job, source_file)

    def _execute(self, job: GEOJob, source_file: Path) -> None:
        try:
            result = GEOPipeline(output_dir=str(job.output_dir)).run(
                input_path=str(source_file)
            )
        except Exception as exc:
            job.status = "error"
            job.message = str(exc)
            job.updated_at = _now_iso()
            self._save()
            return

        if result.get("status") != "success":
            job.status = "error"
            job.message = result.get("message", "GEO pipeline failed")
            job.updated_at = _now_iso()
            self._save()
            return

        job.status = "success"
        job.output_files = result.get("result", {}).get("files", [])
        job.updated_at = _now_iso()
        self._save()

    def get_job(self, task_id: str) -> Optional[GEOJob]:
        return self.jobs.get(task_id)

    def list_jobs(self) -> List[GEOJob]:
        return sorted(
            self.jobs.values(),
            key=lambda job: job.created_at or "",
            reverse=True,
        )

    def get_project_detail(self, task_id: str) -> Optional[Dict[str, Any]]:
        job = self.get_job(task_id)
        if not job:
            return None
        detail = job.to_dict()
        detail["analysis"] = self._load_analysis(job)
        return detail

    def get_output_path(self, task_id: str, filename: str) -> Optional[Path]:
        job = self.get_job(task_id)
        if not job or not job.output_dir:
            return None
        output_dir = Path(job.output_dir).resolve()
        target = (output_dir / Path(filename).name).resolve()
        if output_dir not in target.parents:
            return None
        if not target.is_file():
            return None
        return target

    def get_stats(self) -> Dict[str, int]:
        jobs = self.list_jobs()
        return {
            "total": len(jobs),
            "completed": sum(1 for job in jobs if job.status == "success"),
            "processing": sum(
                1 for job in jobs if job.status in {"queued", "running"}
            ),
            "failed": sum(1 for job in jobs if job.status == "error"),
        }

    def _load_analysis(self, job: GEOJob) -> Dict[str, Any]:
        output_dir = Path(job.output_dir)
        loaded: Dict[str, Any] = {}
        for key, filename in ANALYSIS_FILES.items():
            path = output_dir / filename
            if path.is_file():
                try:
                    loaded[key] = json.loads(path.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    loaded[key] = {}
        return loaded
