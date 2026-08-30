"""GEO service layer: project registry, background tasks and pipeline execution."""

from __future__ import annotations

import json
import shutil
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from config.settings import (
    PROJECTS_FILE,
    STORAGE_PATH,
    TASK_OUTPUT_DIR,
    UPLOAD_DIR,
)
from database.repositories import (
    load_project_records,
    save_project_records,
)
from workflow.pipeline import GEOPipeline

STORAGE_DIR = STORAGE_PATH
LEGACY_PROJECTS_FILE = STORAGE_DIR / "legacy_projects.json"

ACTIVE_STATUSES = {"CREATED", "PARSING", "ANALYZING", "GENERATING"}
STATUS_PROGRESS = {
    "CREATED": 10,
    "PARSING": 25,
    "ANALYZING": 60,
    "GENERATING": 85,
    "COMPLETED": 100,
    "FAILED": 100,
}
STATUS_ALIASES = {
    "queued": "CREATED",
    "running": "ANALYZING",
    "success": "COMPLETED",
    "error": "FAILED",
}

ANALYSIS_FILES = {
    "customer_profile": "customer_profile.json",
    "document_markdown": "document_markdown.json",
    "knowledge_extract": "knowledge_extract.json",
    "company_profile": "company_profile.json",
    "business_analysis": "business_analysis.json",
    "keywords": "keywords.json",
    "personas": "personas.json",
    "content_plan": "content_plan.json",
    "strategy_plan": "strategy_plan.json",
    "monitor_report": "monitor_report.json",
    "geo_score": "geo_score.json",
    "pipeline_result": "pipeline_result.json",
}


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


@dataclass
class GEOJob:
    task_id: str
    status: str = "CREATED"
    customer_name: str = ""
    website: str = ""
    industry: str = ""
    owner: str = ""
    source_file: str = ""
    output_dir: str = ""
    output_files: List[str] = field(default_factory=list)
    error_message: str = ""
    created_time: str = ""
    updated_time: str = ""

    def to_dict(self) -> Dict[str, Any]:
        reports = [
            file_path
            for file_path in self.output_files
            if file_path.lower().endswith((".docx", ".pdf"))
        ]
        return {
            "project_id": self.task_id,
            "id": self.task_id,
            "task_id": self.task_id,
            "status": self.status,
            "progress": STATUS_PROGRESS.get(self.status, 10),
            "customer_name": self.customer_name,
            "website": self.website,
            "industry": self.industry,
            "owner": self.owner,
            "source_file": self.source_file,
            "output_dir": self.output_dir,
            "output_files": self.output_files,
            "files": self.output_files,
            "reports": reports,
            "error_message": self.error_message,
            "message": self.error_message,
            "created_time": self.created_time,
            "updated_time": self.updated_time,
            "created_at": self.created_time,
            "updated_at": self.updated_time,
        }


class GeoService:
    """In-memory project registry persisted to a local JSON file."""

    def __init__(self) -> None:
        self.jobs: Dict[str, GEOJob] = {}
        self._lock = threading.RLock()
        self._load()

    def _load(self) -> None:
        raw_items = load_project_records()
        for item in raw_items:
            job = self._job_from_dict(item)
            self.jobs[job.task_id] = job

        if LEGACY_PROJECTS_FILE.exists() and not self.jobs:
            try:
                raw_items = json.loads(LEGACY_PROJECTS_FILE.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                raw_items = []
            for item in raw_items:
                job = self._job_from_dict(item)
                self.jobs[job.task_id] = job
            self._save()

    def _job_from_dict(self, item: Dict[str, Any]) -> GEOJob:
        task_id = str(item.get("id") or item.get("task_id") or "")
        status = STATUS_ALIASES.get(str(item.get("status", "")), str(item.get("status", "CREATED")))
        now = _now_iso()
        return GEOJob(
            task_id=task_id,
            status=status or "CREATED",
            customer_name=item.get("customer_name", ""),
            website=item.get("website", ""),
            industry=item.get("industry", ""),
            owner=item.get("owner", ""),
            source_file=item.get("source_file", ""),
            output_dir=item.get("output_dir", ""),
            output_files=list(item.get("output_files", []) or []),
            error_message=item.get("error_message") or item.get("message", ""),
            created_time=item.get("created_time") or item.get("created_at") or now,
            updated_time=item.get("updated_time") or item.get("updated_at") or now,
        )

    def _resolve_source_file(self, job: GEOJob) -> Optional[Path]:
        """Find the uploaded source file even when an older record stores a stale path."""
        candidates: List[Path] = []
        if job.source_file:
            candidates.append(Path(job.source_file))

        upload_dir = UPLOAD_DIR / job.task_id
        for suffix in (".xlsx", ".docx", ".pdf", ".txt"):
            candidates.append(upload_dir / f"source{suffix}")
        if upload_dir.is_dir():
            candidates.extend(sorted(upload_dir.iterdir()))

        legacy_upload_dir = STORAGE_PATH.parent / "geo-production-tool" / "storage" / "uploads" / job.task_id
        if legacy_upload_dir.is_dir():
            candidates.append(legacy_upload_dir)
            candidates.extend(sorted(legacy_upload_dir.iterdir()))

        for candidate in candidates:
            if candidate.is_file():
                return candidate
        return None

    def _save(self) -> None:
        PROJECTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            payload = [job.to_dict() for job in self.jobs.values()]
            save_project_records(payload)

    def start_analysis(
        self,
        source_file: Path,
        task_id: Optional[str] = None,
        customer_name: str = "",
        website: str = "",
        industry: str = "",
        owner: str = "",
    ) -> GEOJob:
        current_id = task_id or uuid.uuid4().hex[:12]
        now = _now_iso()
        job = GEOJob(
            task_id=current_id,
            status="CREATED",
            customer_name=customer_name,
            website=website,
            industry=industry,
            owner=owner,
            source_file=str(source_file),
            output_dir=str(TASK_OUTPUT_DIR / current_id),
            created_time=now,
            updated_time=now,
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
        owner: str = "",
    ) -> GEOJob:
        current_id = task_id or uuid.uuid4().hex[:12]
        now = _now_iso()
        job = GEOJob(
            task_id=current_id,
            status="CREATED",
            customer_name=customer_name,
            website=website,
            industry=industry,
            owner=owner,
            source_file=str(source_file),
            output_dir=str(TASK_OUTPUT_DIR / current_id),
            created_time=now,
            updated_time=now,
        )
        self.jobs[current_id] = job
        self._save()
        self._set_status(job, "PARSING")
        self._execute(job, source_file, lambda status: self._set_status(job, status))
        return job

    def create_project(
        self,
        customer_name: str,
        website: str = "",
        industry: str = "",
        owner: str = "",
        source_file: Optional[Path] = None,
        run_immediately: bool = False,
    ) -> GEOJob:
        """Create a project record without binding to a source file by default."""
        current_id = uuid.uuid4().hex[:12]
        now = _now_iso()
        job = GEOJob(
            task_id=current_id,
            status="CREATED",
            customer_name=customer_name,
            website=website,
            industry=industry,
            owner=owner,
            source_file=str(source_file) if source_file else "",
            output_dir=str(TASK_OUTPUT_DIR / current_id),
            created_time=now,
            updated_time=now,
        )
        self.jobs[current_id] = job
        self._save()
        if run_immediately and source_file is not None:
            thread = threading.Thread(
                target=self._run_async,
                args=(job, Path(source_file)),
                daemon=True,
            )
            thread.start()
        return job

    def _run_async(self, job: GEOJob, source_file: Path) -> None:
        self._set_status(job, "PARSING")
        self._execute(job, source_file, lambda status: self._set_status(job, status))

    def _execute(
        self,
        job: GEOJob,
        source_file: Path,
        status_callback: Optional[Callable[[str], None]] = None,
    ) -> None:
        try:
            result = GEOPipeline(output_dir=str(job.output_dir)).run(
                input_path=str(source_file),
                status_callback=status_callback,
            )
        except Exception as exc:
            self._set_status(job, "FAILED", str(exc))
            return

        if result.get("status") != "success":
            self._set_status(
                job,
                "FAILED",
                result.get("message", "GEO pipeline failed"),
            )
            return

        files = result.get("result", {}).get("files", [])
        self._set_status(job, "COMPLETED")
        with self._lock:
            if job.task_id in self.jobs:
                job.output_files = files
                job.updated_time = _now_iso()
                self._save()

    def _set_status(
        self,
        job: GEOJob,
        status: str,
        error_message: Optional[str] = None,
    ) -> None:
        with self._lock:
            if job.task_id not in self.jobs:
                return
            job.status = status
            job.updated_time = _now_iso()
            if error_message is not None:
                job.error_message = error_message
            elif status in {"CREATED", "COMPLETED"}:
                job.error_message = ""
            if status == "CREATED":
                job.output_files = []
            self._save()

    def rerun_project(self, task_id: str) -> tuple[Optional[GEOJob], Optional[str]]:
        job = self.get_job(task_id)
        if not job:
            return None, "not_found"
        if job.status in ACTIVE_STATUSES:
            return None, "active"
        source_path = self._resolve_source_file(job)
        if source_path is None:
            return None, "missing_source"

        old_output_dir = Path(job.output_dir or "")
        if old_output_dir.is_dir():
            shutil.rmtree(old_output_dir, ignore_errors=True)
        new_output_dir = TASK_OUTPUT_DIR / job.task_id
        if new_output_dir.is_dir():
            shutil.rmtree(new_output_dir, ignore_errors=True)
        with self._lock:
            job.source_file = str(source_path)
            job.output_dir = str(new_output_dir)
            job.output_files = []
            job.error_message = ""
            job.updated_time = _now_iso()
            self._save()

        self._set_status(job, "CREATED")
        thread = threading.Thread(
            target=self._run_async,
            args=(job, source_path),
            daemon=True,
        )
        thread.start()
        return job, None

    def update_project(
        self,
        task_id: str,
        owner: Optional[str] = None,
        website: Optional[str] = None,
        industry: Optional[str] = None,
    ) -> tuple[Optional[GEOJob], Optional[str]]:
        job = self.get_job(task_id)
        if not job:
            return None, "not_found"
        if job.status in ACTIVE_STATUSES:
            return None, "active"
        with self._lock:
            if owner is not None:
                job.owner = owner
            if website is not None:
                job.website = website
            if industry is not None:
                job.industry = industry
            job.updated_time = _now_iso()
            self._save()
        return job, None

    def delete_project(self, task_id: str) -> tuple[bool, Optional[str]]:
        job = self.get_job(task_id)
        if not job:
            return False, "not_found"
        if job.status in ACTIVE_STATUSES:
            return False, "active"

        with self._lock:
            self.jobs.pop(task_id, None)
            self._save()

        output_dir = Path(job.output_dir or "")
        upload_dir = UPLOAD_DIR / task_id
        if output_dir.is_dir() and TASK_OUTPUT_DIR in output_dir.parents:
            shutil.rmtree(output_dir, ignore_errors=True)
        if upload_dir.is_dir() and UPLOAD_DIR in upload_dir.parents:
            shutil.rmtree(upload_dir, ignore_errors=True)
        return True, None

    def get_job(self, task_id: str) -> Optional[GEOJob]:
        return self.jobs.get(task_id)

    def list_jobs(self) -> List[GEOJob]:
        return sorted(
            self.jobs.values(),
            key=lambda job: job.created_time or "",
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
        keyword_count = 0
        report_count = 0
        score_values = []
        for job in jobs:
            analysis = self._load_analysis(job)
            keyword_count += self._count_keywords(analysis)
            report_count += len(job.to_dict().get("reports", []))
            score = self._extract_score(analysis)
            if score is not None:
                score_values.append(score)
        return {
            "total": len(jobs),
            "completed": sum(1 for job in jobs if job.status == "COMPLETED"),
            "processing": sum(1 for job in jobs if job.status in ACTIVE_STATUSES),
            "failed": sum(1 for job in jobs if job.status == "FAILED"),
            "keyword_count": keyword_count,
            "report_count": report_count,
            "avg_geo_score": round(
                sum(score_values) / len(score_values), 1
            )
            if score_values
            else 0,
        }

    def _count_keywords(self, analysis: Dict[str, Any]) -> int:
        keywords = analysis.get("keywords", {})
        body = keywords.get("result", keywords)
        return len(body.get("keywords", []))

    def _extract_score(self, analysis: Dict[str, Any]) -> Optional[int]:
        score_item = analysis.get("geo_score", {})
        body = score_item.get("result", score_item)
        value = body.get("score")
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

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
