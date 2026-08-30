"""Factory for storage backends and repositories."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from config.settings import STORAGE_BACKEND
from database.base import StorageBackend
from database.json_backend import JsonStorageBackend

_backend: Optional[StorageBackend] = None


def get_storage_backend() -> StorageBackend:
    global _backend
    if _backend is not None:
        return _backend
    if STORAGE_BACKEND == "json":
        _backend = JsonStorageBackend()
    else:
        _backend = JsonStorageBackend()
    return _backend


def read_collection(collection: str) -> List[Dict[str, Any]]:
    return get_storage_backend().read_collection(collection)


def write_collection(collection: str, records: List[Dict[str, Any]]) -> None:
    get_storage_backend().write_collection(collection, records)
