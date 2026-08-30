"""Thread-safe JSON storage for GEO analysis projects."""

from __future__ import annotations

import json
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .schemas.geo_schema import GEOProject

DEFAULT_PROJECTS_FILE = (
    Path(__file__).resolve().parents[2]
    / "storage"
    / "geo_analysis"
    / "projects.json"
)


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


class GeoProjectStore:
    """Local JSON project registry with an interface suitable for later DB swap."""

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = Path(path or DEFAULT_PROJECTS_FILE)
        self._lock = threading.RLock()
        self._projects: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.is_file():
            return
        try:
            records = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            records = []
        with self._lock:
            self._projects = {}
            for record in records if isinstance(records, list) else []:
                if record.get("id"):
                    self._projects[str(record["id"])] = record

    def _save(self) -> None:
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temp_path = self.path.with_suffix(".json.tmp")
            temp_path.write_text(
                json.dumps(list(self._projects.values()), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            temp_path.replace(self.path)

    def create(
        self,
        name: str,
        source: str = "",
        initial: Optional[Dict[str, Any]] = None,
    ) -> GEOProject:
        now = _now_iso()
        project = GEOProject(
            id=uuid.uuid4().hex[:12],
            name=name,
            source=source,
            status="PENDING",
            progress=0,
            created_at=now,
            updated_at=now,
        )
        with self._lock:
            self._projects[project.id] = project.model_dump()
            self._save()
        return project

    def update(self, project_id: str, **fields: Any) -> Optional[GEOProject]:
        with self._lock:
            project = self._projects.get(project_id)
            if not project:
                return None
            for key, value in fields.items():
                if value is not None:
                    project[key] = value
            project["updated_at"] = _now_iso()
            self._save()
            return GEOProject(**project)

    def get(self, project_id: str) -> Optional[GEOProject]:
        with self._lock:
            project = self._projects.get(project_id)
            return GEOProject(**project) if project else None

    def list(self) -> List[GEOProject]:
        with self._lock:
            return [
                GEOProject(**record)
                for record in sorted(
                    self._projects.values(),
                    key=lambda item: item.get("created_at", ""),
                    reverse=True,
                )
            ]

    def delete(self, project_id: str) -> bool:
        with self._lock:
            existed = self._projects.pop(project_id, None) is not None
            if existed:
                self._save()
            return existed


_default_store: Optional[GeoProjectStore] = None


def get_geo_project_store(path: Optional[Path] = None) -> GeoProjectStore:
    global _default_store
    if path is not None:
        return GeoProjectStore(path=path)
    if _default_store is None:
        _default_store = GeoProjectStore()
    return _default_store
