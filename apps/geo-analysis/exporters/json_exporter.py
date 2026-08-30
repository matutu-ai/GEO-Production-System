"""JSON analysis data exporter."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict

LOGGER = logging.getLogger(__name__)


def export_json(result: Dict[str, Any], output_path: Path) -> Path:
    """Write the full GEO analysis result as JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    LOGGER.info("JSON data written: %s", output_path)
    return output_path
