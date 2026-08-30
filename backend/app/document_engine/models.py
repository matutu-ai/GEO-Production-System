"""Pydantic models for document ingestion and knowledge extraction."""

from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    chunk_id: str
    text: str
    section: str = ""
    chunk_type: str = "general"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentResult(BaseModel):
    filename: str
    content: str
    format: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    chunks: List[DocumentChunk] = Field(default_factory=list)


class CompanyKnowledge(BaseModel):
    company: Dict[str, Any] = Field(default_factory=dict)
    products: List[Dict[str, Any]] = Field(default_factory=list)
    market: Dict[str, Any] = Field(default_factory=dict)
    raw_document: str = ""
