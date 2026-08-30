"""Article input and normalized analysis schemas."""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class SourceType(str, Enum):
    URL = "url"
    HTML = "html"
    MARKDOWN = "markdown"
    TXT = "txt"
    TEXT = "text"


class ArticleInput(BaseModel):
    name: str = "GEO Analysis Project"
    source: str = ""
    source_type: SourceType = SourceType.TEXT
    content: str = ""
    product_description: str = ""
    company_info: str = ""


class ArticleAnalysis(BaseModel):
    title: str = ""
    summary: str = ""
    topics: List[str] = Field(default_factory=list)
    entities: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    source: str = ""


class Entity(BaseModel):
    name: str
    type: str
    confidence: int = Field(ge=0, le=100)
    mentions: int = Field(default=1, ge=1)


class EntityGraph(BaseModel):
    entities: List[Entity] = Field(default_factory=list)
    relationships: List[dict] = Field(default_factory=list)


class Keyword(BaseModel):
    keyword: str
    type: str
    intent: str
    priority: str = "B"
    cluster: str = ""


class KeywordCluster(BaseModel):
    cluster: str
    primary: List[str] = Field(default_factory=list)
    secondary: List[str] = Field(default_factory=list)
    semantic: List[str] = Field(default_factory=list)
    keywords: List[Keyword] = Field(default_factory=list)


class SearchIntent(BaseModel):
    intent: str
    label: str
    description: str
    keywords: List[str] = Field(default_factory=list)
    share: int = Field(ge=0, le=100)


class FrameworkSection(BaseModel):
    heading: str
    level: int = Field(ge=1, le=4)
    purpose: str = ""


class ContentFramework(BaseModel):
    structure: List[FrameworkSection] = Field(default_factory=list)
    faq: List[dict] = Field(default_factory=list)
    schema_markup: str = Field(default="", validation_alias="schema", serialization_alias="schema")
    recommendations: List[str] = Field(default_factory=list)


class GEOScore(BaseModel):
    entity_coverage: int = Field(ge=0, le=100)
    keyword_coverage: int = Field(ge=0, le=100)
    intent_match: int = Field(ge=0, le=100)
    content_structure: int = Field(ge=0, le=100)
    authority_score: int = Field(ge=0, le=100)
    total: int = Field(ge=0, le=100)
