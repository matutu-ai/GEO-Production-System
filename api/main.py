"""GEO Production Tool FastAPI entry point."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Dict

from fastapi import FastAPI, File, HTTPException, UploadFile

from services.geo_service import GeoService, STORAGE_DIR

BASE_DIR = Path(__file__).resolve().parents[1]
ALLOWED_EXTENSIONS = {".xlsx", ".docx", ".pdf"}

service = GeoService()
app = FastAPI(
    title="GEO Production Tool API",
    description="内部 GEO 交付工具 API，上传客户资料后运行完整分析流水线。",
    version="1.5",
)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "running", "version": "1.5"}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)) -> Dict:
    filename = file.filename or "customer.xlsx"
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="unsupported file type, expected .xlsx/.docx/.pdf",
        )

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="uploaded file is empty")

    task_id = uuid.uuid4().hex[:12]
    upload_dir = STORAGE_DIR / "uploads" / task_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    source_path = upload_dir / f"source{suffix}"
    source_path.write_bytes(content)

    job = service.run_analysis(source_path, task_id=task_id)
    return job.to_dict()


@app.get("/result/{task_id}")
def get_result(task_id: str) -> Dict:
    job = service.get_job(task_id)
    if not job:
        raise HTTPException(status_code=404, detail="task not found")
    return job.to_dict()
