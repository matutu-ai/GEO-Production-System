"""Workflow nodes shared by the GEO pipeline."""

from __future__ import annotations

from typing import Any, Dict

from app.document_engine.document_pipeline import DocumentPipeline


class DocumentParserNode:
    """Parse an uploaded enterprise file into normalized Markdown and chunks."""

    def __init__(self, chunk_size: int = 1000, overlap: int = 100) -> None:
        self.pipeline = DocumentPipeline(chunk_size=chunk_size, overlap=overlap)

    def run(self, file_path: str) -> Dict[str, Any]:
        return self.pipeline.process(file_path)
