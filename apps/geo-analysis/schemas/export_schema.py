"""Export manifest schema."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class ExportFile(BaseModel):
    filename: str
    path: str
    content_type: str
    size: int = 0


class ExportManifest(BaseModel):
    project_id: str
    files: List[ExportFile] = Field(default_factory=list)
