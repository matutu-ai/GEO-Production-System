from pathlib import Path

from geo_analysis.storage import GeoProjectStore
from geo_analysis.workflow.geo_pipeline import GEOAnalysisPipeline


def test_pipeline_completes_and_writes_project_files(tmp_path, sample_input):
    export_dir = tmp_path / "exports"
    project = GeoProjectStore(tmp_path / "projects.json").create(
        "Pipeline Test",
        "https://example.com/article",
    )
    progress = []

    output = GEOAnalysisPipeline(output_dir=export_dir).run(
        project.id,
        sample_input,
        lambda stage, value: progress.append((stage, value)),
    )

    assert output["status"] == "success"
    assert output["svg_file"].endswith("architecture.svg")
    assert (progress[-1]) == ("COMPLETED", 100)
    assert (export_dir / project.id / "analysis.json").exists()
    assert (export_dir / project.id / "architecture.svg").exists()
