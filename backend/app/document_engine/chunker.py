"""Text chunking helpers for enterprise knowledge ingestion."""

from __future__ import annotations

import re
from typing import Dict, List


class TextChunker:
    def __init__(self, chunk_size: int = 1000, overlap: int = 100) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if overlap < 0 or overlap >= chunk_size:
            raise ValueError("overlap must be between 0 and chunk_size")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, content: str, section: str = "") -> List[Dict[str, str]]:
        if not content or not content.strip():
            return []

        blocks = self._split_sections(content)
        chunks: List[Dict[str, str]] = []
        for heading, body in blocks:
            for index, text in enumerate(self._split_length(body)):
                chunks.append(
                    {
                        "chunk_id": f"chunk-{len(chunks) + 1:04d}",
                        "text": text.strip(),
                        "section": heading or section,
                    }
                )
        return [chunk for chunk in chunks if chunk["text"]]

    def _split_sections(self, content: str) -> List[tuple]:
        lines = content.splitlines()
        blocks: List[tuple] = []
        current_heading = ""
        current_lines: List[str] = []

        def flush() -> None:
            nonlocal current_lines
            body = "\n".join(current_lines).strip()
            if body:
                blocks.append((current_heading, body))
            current_lines = []

        heading_pattern = re.compile(r"^(#{1,6}\s+.+)$")
        label_pattern = re.compile(
            r"^(公司简介|企业介绍|公司介绍|产品介绍|产品体系|产品|服务|优势|案例|"
            r"客户|客户群体|应用场景|痛点|解决方案|市场|AI问答问题)[:：]?$"
        )
        row_label_pattern = re.compile(
            r"^(公司名称|企业名称|客户名称|官网|行业|主营产品|产品|服务|优势|案例|客户)"
            r"[:：]"
        )

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            heading_match = heading_pattern.match(stripped) or label_pattern.match(stripped)
            row_match = row_label_pattern.match(stripped)
            if heading_match:
                flush()
                current_heading = re.sub(r"^#{1,6}\s+", "", heading_match.group(1)).strip()
                current_lines.append(stripped)
            elif row_match:
                flush()
                current_heading = row_match.group(1)
                current_lines.append(stripped)
            else:
                current_lines.append(stripped)
        flush()
        return blocks

    def _split_length(self, text: str) -> List[str]:
        if len(text) <= self.chunk_size:
            return [text]
        parts = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            part = text[start:end].strip()
            if part:
                parts.append(part)
            if end >= len(text):
                break
            start = max(end - self.overlap, start + 1)
        return parts
