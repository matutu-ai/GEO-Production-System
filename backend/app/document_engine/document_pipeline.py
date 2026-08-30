"""Enterprise document pipeline: parse, normalize, chunk and classify."""

from __future__ import annotations

from typing import Any, Dict, List

from app.document_engine.chunker import TextChunker
from app.document_engine.markitdown_parser import MarkItDownParser


class DocumentPipeline:
    def __init__(self, chunk_size: int = 1000, overlap: int = 100) -> None:
        self.parser = MarkItDownParser()
        self.chunker = TextChunker(chunk_size=chunk_size, overlap=overlap)

    def process(self, file_path: str) -> Dict[str, Any]:
        document = self.parser.convert(file_path)
        raw_chunks = self.chunker.chunk(document["content"])
        chunks = [self._classify_chunk(chunk) for chunk in raw_chunks]
        return {
            "document": document,
            "chunks": chunks,
            "knowledge": self._quick_knowledge(document["content"]),
        }

    @staticmethod
    def _classify_chunk(chunk: Dict[str, Any]) -> Dict[str, Any]:
        text = f"{chunk.get('section', '')}\n{chunk.get('text', '')}"
        section = chunk.get("section", "")
        if any(keyword in text for keyword in ("公司", "企业", "简介")):
            chunk_type = "company"
        elif "案例" in text or "客户" in text:
            chunk_type = "case"
        elif any(keyword in text for keyword in ("产品", "设备", "解决方案")):
            chunk_type = "product"
        else:
            chunk_type = "general"
        chunk["chunk_type"] = chunk_type
        chunk["section"] = section
        return chunk

    @staticmethod
    def _quick_knowledge(content: str) -> Dict[str, List[str]]:
        company = DocumentPipeline._extract_values(content, ["公司名称", "企业名称", "公司"])
        products = DocumentPipeline._extract_values(content, ["产品", "主营产品"])
        services = DocumentPipeline._extract_values(content, ["服务"])
        cases = DocumentPipeline._extract_values(content, ["案例"])
        customers = DocumentPipeline._extract_values(content, ["客户", "客户群体"])
        return {
            "company": company,
            "products": products,
            "services": services,
            "cases": cases,
            "customers": customers,
        }

    @staticmethod
    def _extract_values(content: str, labels: List[str]) -> List[str]:
        import re

        values = []
        for label in labels:
            matches = re.findall(
                rf"{re.escape(label)}\s*[:：]\s*([^\n]+)",
                content,
                flags=re.MULTILINE,
            )
            for match in matches:
                for item in re.split(r"[、,，;；/|]+", match.strip()):
                    if item and item not in values:
                        values.append(item.strip())
        return values
