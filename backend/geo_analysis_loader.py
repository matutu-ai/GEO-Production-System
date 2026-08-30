"""Loader for the isolated apps/geo-analysis Python package.

The module directory uses a hyphen and is intentionally independent from the
existing backend agent package, so FastAPI imports it under the `geo_analysis`
package name.
"""

from __future__ import annotations

import importlib
import sys
import types
from pathlib import Path

GEO_ANALYSIS_ROOT = Path(__file__).resolve().parents[1] / "apps" / "geo-analysis"


def _ensure_package():
    package = sys.modules.get("geo_analysis")
    if package is not None:
        return package
    package = types.ModuleType("geo_analysis")
    package.__path__ = [str(GEO_ANALYSIS_ROOT)]
    package.__name__ = "geo_analysis"
    sys.modules["geo_analysis"] = package
    return package


def get_geo_module(module_name: str):
    _ensure_package()
    return importlib.import_module(f"geo_analysis.{module_name}")
