"""Core GEO analysis result schema."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .article_schema import (
    ArticleAnalysis,
    ContentFramework,
    EntityGraph,
    GEOScore,
    KeywordCluster,
    SearchIntent,
)


class GEOAnalysisResult(BaseModel):
    article: ArticleAnalysis = Field(default_factory=ArticleAnalysis)
    entities: EntityGraph = Field(default_factory=EntityGraph)
    keyword_clusters: List[KeywordCluster] = Field(default_factory=list)
    intents: List[SearchIntent] = Field(default_factory=list)
    framework: ContentFramework = Field(default_factory=ContentFramework)
    score: GEOScore = Field(default_factory=GEOScore)
    files: List[str] = Field(default_factory=list)


class GEOProject(BaseModel):
    id: str
    name: str
    source: str = ""
    status: str = "PENDING"
    progress: int = Field(default=0, ge=0, le=100)
    analysis_result: Dict[str, Any] = Field(default_factory=dict)
    svg_file: str = ""
    created_at: str = ""
    updated_at: str = ""


class GEOProjectUpdate(BaseModel):
    status: Optional[str] = None
    progress: Optional[int] = None
    analysis_result: Optional[Dict[str, Any]] = None
    svg_file: Optional[str] = None
    error: Optional[str] = None
