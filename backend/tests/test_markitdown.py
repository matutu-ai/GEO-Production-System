"""Tests for the MarkItDown document parser wrapper."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.document_engine.markitdown_parser import (
    MarkItDownParser,
    UnsupportedFormatError,
)

INPUT_DIR = Path(__file__).resolve().parents[1] / "input"


@pytest.fixture
def parser() -> MarkItDownParser:
    return MarkItDownParser()


def test_convert_docx(parser: MarkItDownParser) -> None:
    result = parser.convert(str(INPUT_DIR / "demo_customer.docx"))

    assert result["filename"] == "demo_customer.docx"
    assert result["format"] == "docx"
    assert "邦胜工业设备有限公司" in result["content"]
    assert result["metadata"]["engine"] in {"markitdown", "fallback"}


def test_convert_pdf(parser: MarkItDownParser) -> None:
    result = parser.convert(str(INPUT_DIR / "demo_customer.pdf"))

    assert result["filename"] == "demo_customer.pdf"
    assert result["format"] == "pdf"
    assert "自动包装设备" in result["content"]
    assert result["metadata"]["size"] > 0


def test_missing_file_raises_file_not_found(parser: MarkItDownParser) -> None:
    with pytest.raises(FileNotFoundError):
        parser.convert(str(INPUT_DIR / "not-exist.docx"))


def test_unsupported_format_raises_error(parser: MarkItDownParser, tmp_path: Path) -> None:
    unsupported = tmp_path / "sample.png"
    unsupported.write_bytes(b"not-a-document")

    with pytest.raises(UnsupportedFormatError):
        parser.convert(str(unsupported))
