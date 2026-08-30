from pathlib import Path

from geo_analysis.exporters.export_service import export_all
from geo_analysis.workflow.geo_pipeline import GEOAnalysisPipeline


def test_export_all_writes_full_package(tmp_path, sample_input):
    pipeline = GEOAnalysisPipeline(output_dir=tmp_path / "exports")
    output = pipeline.run("export-test", sample_input)

    assert output["status"] == "success"
    files = [Path(path).name for path in output["files"]]
    assert "analysis.json" in files
    assert "report.md" in files
    assert "report.html" in files
    assert "report.pdf" in files
    assert "architecture.svg" in files
    assert "architecture.png" in files

    export_dir = tmp_path / "exports" / "export-test"
    assert (export_dir / "report.pdf").stat().st_size > 1000
    assert (export_dir / "report.html").read_text(encoding="utf-8").startswith("<!doctype html>")
    assert "<svg" in (export_dir / "report.html").read_text(encoding="utf-8")
