"""Article analyzer agent.

The agent normalizes article input from URL, HTML, Markdown or plain text into
a structured analysis that the rest of the GEO pipeline can consume.
"""

from __future__ import annotations

import logging
import re
from collections import Counter
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from ..schemas.article_schema import ArticleAnalysis, ArticleInput, SourceType

LOGGER = logging.getLogger(__name__)

STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "of",
    "for",
    "to",
    "in",
    "on",
    "with",
    "is",
    "are",
    "it",
    "this",
    "that",
    "how",
    "what",
    "why",
    "can",
    "your",
    "you",
    "we",
    "our",
    "about",
    "more",
    "from",
    "by",
    "as",
    "at",
    "be",
}


class ArticleAnalyzerAgent:
    """Normalize and analyze an article before GEO processing."""

    def run(self, input_data: dict) -> dict:
        try:
            payload = ArticleInput(**input_data)
            source_type = self._resolve_source_type(payload)
            content, metadata = self._load_content(payload, source_type)
            article = self._analyze(payload, content, source_type, metadata)
            return {
                "task": "article_analysis",
                "status": "success",
                "confidence": 90,
                "result": article.model_dump(),
                "next_action": "entity_analysis",
            }
        except Exception as exc:
            LOGGER.exception("ArticleAnalyzerAgent failed")
            return {
                "task": "article_analysis",
                "status": "error",
                "confidence": 0,
                "result": {},
                "next_action": "fix_input",
                "message": str(exc),
            }

    def _resolve_source_type(self, payload: ArticleInput) -> SourceType:
        if payload.source_type != SourceType.TEXT:
            return payload.source_type
        if payload.content.strip():
            content = payload.content.strip()
            if "<html" in content[:2000].lower() or "<body" in content[:2000].lower():
                return SourceType.HTML
            if re.search(r"(?m)^#{1,6}\s", content):
                return SourceType.MARKDOWN
            return SourceType.TEXT
        source = payload.source.strip()
        if source.startswith(("http://", "https://")):
            return SourceType.URL
        return SourceType.TEXT

    def _load_content(self, payload: ArticleInput, source_type: SourceType):
        if source_type == SourceType.URL:
            return self._fetch_url(payload.source)
        content = payload.content.strip()
        if not content:
            content = payload.source.strip()
        if source_type == SourceType.HTML:
            soup = BeautifulSoup(content, "html.parser")
            text = soup.get_text("\n", strip=True)
            title = soup.title.string.strip() if soup.title and soup.title.string else payload.name
            return text, {"title": title, "format": "html"}
        if source_type == SourceType.MARKDOWN:
            text = re.sub(r"^#{1,6}\s*", "", content, flags=re.MULTILINE)
            text = re.sub(r"[*_`>]", "", text)
            first_heading = re.search(r"(?m)^#{1,6}\s*(.+)$", content)
            title = first_heading.group(1).strip() if first_heading else payload.name
            return text, {"title": title, "format": "markdown"}
        title = payload.name
        if payload.source and not content:
            content = payload.source
        return content, {"title": title, "format": "txt"}

    def _fetch_url(self, url: str):
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("invalid article URL")
        response = requests.get(url, timeout=15, headers={"User-Agent": "GEOAnalysisBot/1.0"})
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        if "html" in content_type.lower():
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text("\n", strip=True)
            title = soup.title.string.strip() if soup.title and soup.title.string else parsed.netloc
            return text, {"title": title, "format": "html", "url": url}
        return response.text, {"title": url, "format": "text", "url": url}

    def _analyze(
        self,
        payload: ArticleInput,
        content: str,
        source_type: SourceType,
        metadata: dict,
    ) -> ArticleAnalysis:
        clean_text = self._clean_text(content)
        title = metadata.get("title") or self._guess_title(clean_text, payload.name)
        summary = self._summarize(clean_text)
        topics = self._extract_topics(clean_text, payload, title)
        keywords = self._extract_keywords(clean_text, topics, payload)
        entities = self._extract_entity_candidates(clean_text, payload)
        return ArticleAnalysis(
            title=title,
            summary=summary,
            topics=topics,
            entities=entities,
            keywords=keywords,
            source=payload.source,
        )

    def _clean_text(self, content: str) -> str:
        content = re.sub(r"<[^>]+>", " ", content)
        content = re.sub(r"[#*_`>\[\]()]", " ", content)
        content = re.sub(r"\s+", " ", content)
        return content.strip()

    def _guess_title(self, text: str, fallback: str) -> str:
        sentences = re.split(r"[。!?；\n]", text)
        for sentence in sentences[:5]:
            candidate = sentence.strip().strip(":")
            if 8 <= len(candidate) <= 120:
                return candidate
        return fallback

    def _summarize(self, text: str) -> str:
        sentences = [s.strip() for s in re.split(r"[。!?；\n]", text) if len(s.strip()) > 20]
        if not sentences:
            return text[:180] or "No article content provided."
        return " ".join(sentences[:3])[:400]

    def _extract_topics(self, text: str, payload: ArticleInput, title: str) -> list:
        topics: list[str] = []
        for item in self._split_list(payload.product_description):
            if item and item not in topics:
                topics.append(item)
        for item in self._split_list(payload.company_info):
            if item and item not in topics:
                topics.append(item)

        known_terms = [
            "GEO",
            "AI search",
            "brand",
            "content",
            "keywords",
            "search intent",
            "entity",
            "automation",
            "packaging",
            "industrial",
            "ecommerce",
            "FAQ",
        ]
        for term in known_terms:
            if term.lower() in text.lower() or term.lower() in title.lower():
                topics.append(term)
        topics.append(self._title_topic(title))
        seen = set()
        result = []
        for topic in topics:
            key = topic.strip().lower()
            if key and key not in seen:
                seen.add(key)
                result.append(topic.strip())
        return result[:10]

    def _title_topic(self, title: str) -> str:
        title = title.strip()
        if not title:
            return "content topic"
        words = re.findall(r"[\w\u4e00-\u9fff-]+", title)
        return " ".join(words[-3:]) if len(words) > 3 else title

    def _extract_keywords(self, text: str, topics: list, payload: ArticleInput) -> list:
        words = re.findall(r"[A-Za-z][A-Za-z0-9+#-]{2,}", text.lower())
        counter = Counter(words)
        ranked = [word for word, _ in counter.most_common(80) if word not in STOPWORDS]
        ranked.extend(topics)
        ranked.extend(self._split_list(payload.product_description))
        ranked.extend(self._split_list(payload.company_info))
        seen = set()
        result = []
        for item in ranked:
            key = item.lower().strip()
            if key and key not in seen:
                seen.add(key)
                result.append(item.strip())
            if len(result) >= 20:
                break
        return result

    def _extract_entity_candidates(self, text: str, payload: ArticleInput) -> list:
        candidates = [payload.company_info, payload.product_description]
        for term in ("GEO", "AI", "SEO", "search engine"):
            if term.lower() in text.lower():
                candidates.append(term)
        return [item for item in self._split_list("\n".join(candidates)) if item][:12]

    @staticmethod
    def _split_list(value: str) -> list:
        if not value:
            return []
        return [
            item.strip()
            for item in re.split(r"[\n,，;；、|]+", value)
            if item.strip()
        ]
