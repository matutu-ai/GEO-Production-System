"""Async document upload service backed by the document engine."""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from app.document_engine.document_pipeline import DocumentPipeline
from agents.knowledge_agent.agent import KnowledgeExtractAgent
from config.settings import REPORTS_DIR, STORAGE_PATH
from file_writer import save_json

DOCUMENT_OUTPUT_DIR = STORAGE_PATH / "documents"
STATUS_PROGRESS = {
    "uploading": 0,
    "parsing": 20,
    "extracting": 50,
    "generating": 80,
    "completed": 100,
    "failed": 80,
}


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


@dataclass
class DocumentTask:
    task_id: str
    status: str = "uploading"
    progress: int = 0
    filename: str = ""
    document: Optional[Dict[str, Any]] = None
    knowledge: Optional[Dict[str, Any]] = None
    output_file: str = ""
    error_message: str = ""
    created_time: str = ""
    updated_time: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "id": self.task_id,
            "status": self.status,
            "progress": self.progress,
            "filename": self.filename,
            "document": self.document,
            "knowledge": self.knowledge,
            "output_file": self.output_file,
            "error_message": self.error_message,
            "created_time": self.created_time,
            "updated_time": self.updated_time,
        }


class DocumentService:
    """In-memory async document parsing task registry."""

    def __init__(self) -> None:
        self.tasks: Dict[str, DocumentTask] = {}
        self._lock = threading.RLock()

    def start_upload(self, file_path: Path, original_filename: str = "") -> DocumentTask:
        task_id = uuid.uuid4().hex[:12]
        now = _now_iso()
        task = DocumentTask(
            task_id=task_id,
            status="uploading",
            progress=0,
            filename=original_filename or file_path.name,
            created_time=now,
            updated_time=now,
        )
        with self._lock:
            self.tasks[task_id] = task
        thread = threading.Thread(
            target=self._run,
            args=(task, Path(file_path)),
            daemon=True,
        )
        thread.start()
        return task

    def get_task(self, task_id: str) -> Optional[DocumentTask]:
        return self.tasks.get(task_id)

    def _run(self, task: DocumentTask, file_path: Path) -> None:
        try:
            self._set_status(task, "parsing", 20)
            document_result = DocumentPipeline().process(str(file_path))

            self._set_status(task, "extracting", 50)
            knowledge = KnowledgeExtractAgent().run(
                {
                    "document": document_result,
                    "customer_profile": {},
                    "raw_information": document_result.get("document", {}).get(
                        "content", ""
                    ),
                }
            )
            task.document = document_result
            task.knowledge = knowledge

            self._set_status(task, "generating", 80)
            output_dir = DOCUMENT_OUTPUT_DIR / task.task_id
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / "knowledge_extract.json"
            save_json(output_file, knowledge)
            task.output_file = str(output_file)

            self._set_status(task, "completed", 100)
        except Exception as exc:
            self._set_status(task, "failed", 80, str(exc))

    def _set_status(
        self,
        task: DocumentTask,
        status: str,
        progress: int,
        error_message: Optional[str] = None,
    ) -> None:
        with self._lock:
            if task.task_id not in self.tasks:
                return
            task.status = status
            task.progress = progress
            task.updated_time = _now_iso()
            if error_message is not None:
                task.error_message = error_message
