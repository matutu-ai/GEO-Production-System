"""GEO Production Tool V1.3 entry point."""

from __future__ import annotations

from pathlib import Path

from workflow.pipeline import GEOPipeline

BASE_DIR = Path(__file__).resolve().parent


def main() -> None:
    input_path = BASE_DIR / "input" / "demo_customer.xlsx"
    print("GEO Production Tool V1")
    print("开始分析客户资料")

    result = GEOPipeline(output_dir=str(BASE_DIR / "output")).run(
        input_path=str(input_path)
    )
    if result.get("status") != "success":
        print("Pipeline Failed:", result.get("message", "unknown error"))
        return

    print("Input Parser Completed ✓")
    print("Company Agent Completed ✓")
    print("Business Agent Completed ✓")
    print("Keyword Agent Completed ✓")
    print("Persona Agent Completed ✓")
    print("Content Agent Completed ✓")
    print("Strategy Agent Completed ✓")
    print("Report Agent Completed ✓")
    print()
    print("Output Generated:")
    for file_path in result["result"]["files"]:
        print(str(Path(file_path).relative_to(BASE_DIR)))


if __name__ == "__main__":
    main()
