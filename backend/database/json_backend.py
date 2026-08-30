"""JSON storage backend used for local V1 deployments."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from config.settings import PROJECTS_FILE, USERS_FILE
from database.base import StorageBackend


class JsonStorageBackend(StorageBackend):
    """Persist each collection to a JSON file."""

    def __init__(self) -> None:
        self._paths = {
            "projects": PROJECTS_FILE,
            "users": USERS_FILE,
        }

    def read_collection(self, collection: str) -> List[Dict[str, Any]]:
        path = self._paths[collection]
        if not path.is_file():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def write_collection(self, collection: str, records: List[Dict[str, Any]]) -> None:
        path = self._paths[collection]
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_suffix(".json.tmp")
        temp_path.write_text(
            json.dumps(records, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temp_path.replace(path)
