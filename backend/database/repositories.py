"""Repository helpers for projects and users."""

from __future__ import annotations

from typing import Any, Dict, List

from database.registry import read_collection, write_collection


def load_project_records() -> List[Dict[str, Any]]:
    return read_collection("projects")


def save_project_records(records: List[Dict[str, Any]]) -> None:
    write_collection("projects", records)


def load_user_records() -> List[Dict[str, Any]]:
    return read_collection("users")


def save_user_records(records: List[Dict[str, Any]]) -> None:
    write_collection("users", records)
