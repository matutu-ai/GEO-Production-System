"""Storage interface kept deliberately small so JSON can be replaced by SQL."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class StorageBackend(ABC):
    @abstractmethod
    def read_collection(self, collection: str) -> List[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def write_collection(self, collection: str, records: List[Dict[str, Any]]) -> None:
        raise NotImplementedError

