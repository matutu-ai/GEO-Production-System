"""Pytest setup for the isolated GEO Analysis module."""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

GEO_ANALYSIS_ROOT = Path(__file__).resolve().parents[1]


def pytest_configure(config):
    package = sys.modules.get("geo_analysis")
    if package is None:
        package = types.ModuleType("geo_analysis")
        package.__name__ = "geo_analysis"
        sys.modules["geo_analysis"] = package
    package.__path__ = [str(GEO_ANALYSIS_ROOT)]


@pytest.fixture
def sample_input() -> dict:
    return {
        "name": "Automatic Packaging Machines GEO Guide",
        "source": "https://example.com/automatic-packaging-machines",
        "source_type": "text",
        "content": (
            "Industrial automation providers help food and logistics companies reduce "
            "packaging cost. Automatic case erectors, automatic packaging machines and "
            "complete packaging lines improve throughput and reduce labor. Buyers compare "
            "vendors, pricing and implementation plans before requesting a quote."
        ),
        "product_description": "Automatic case erector, Automatic packaging machine, Packaging line",
        "company_info": "Bang Sheng Industrial Equipment Co., Ltd.",
    }
