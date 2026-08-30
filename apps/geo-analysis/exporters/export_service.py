"""Coordinate all GEO analysis report exports."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List

from .html_exporter import export_html
from .json_exporter import export_json
from .markdown_exporter import export_markdown
from .pdf_exporter import export_pdf
from .png_exporter import export_png

LOGGER = logging.getLogger(__name__)

EXPORT_FILES = [
    "analysis.json",
    "report.md",
    "report.html",
    "report.pdf",
    "architecture.svg",
    "architecture.png",
]


def export_all(result: Dict[str, Any], svg: str, output_dir: Path) -> List[str]:
    """Write every export file and return relative paths."""
    output_dir.mkdir(parents=True, exist_ok=True)
    export_json(result, output_dir / "analysis.json")
    export_markdown(result, output_dir / "report.md")
    export_html(result, svg, output_dir / "report.html")
    export_pdf(result, output_dir / "report.pdf")
    (output_dir / "architecture.svg").write_text(svg, encoding="utf-8")
    export_png(svg, output_dir / "architecture.png")

    files = []
    for filename in EXPORT_FILES:
        path = output_dir / filename
        if path.exists() and path.stat().st_size > 0:
            files.append(str(path))
    LOGGER.info("Exports generated: %s", files)
    return files
