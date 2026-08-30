"""GEO Production Tool FastAPI entry point."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Dict

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from services.geo_service import GeoService, STORAGE_DIR

BASE_DIR = Path(__file__).resolve().parents[1]
ALLOWED_EXTENSIONS = {".xlsx", ".docx", ".pdf"}

service = GeoService()
app = FastAPI(
    title="GEO Production Tool API",
    description="GEO Production System V2.0 内部控制台 API。",
    version="2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "running", "version": "2.0"}


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    customer_name: str = Form(""),
    website: str = Form(""),
    industry: str = Form(""),
    sync: bool = Query(False),
) -> Dict:
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

    if sync:
        job = service.run_analysis(
            source_path,
            task_id=task_id,
            customer_name=customer_name,
            website=website,
            industry=industry,
        )
    else:
        job = service.start_analysis(
            source_path,
            task_id=task_id,
            customer_name=customer_name,
            website=website,
            industry=industry,
        )
    return job.to_dict()


@app.get("/projects")
def list_projects() -> Dict:
    return {
        "projects": [job.to_dict() for job in service.list_jobs()],
        "stats": service.get_stats(),
    }


@app.get("/projects/{task_id}")
def get_project(task_id: str) -> Dict:
    detail = service.get_project_detail(task_id)
    if not detail:
        raise HTTPException(status_code=404, detail="project not found")
    return detail


@app.get("/projects/{task_id}/download/{filename}")
def download_project_file(task_id: str, filename: str) -> FileResponse:
    file_path = service.get_output_path(task_id, filename)
    if not file_path:
        raise HTTPException(status_code=404, detail="output file not found")
    return FileResponse(str(file_path), filename=Path(filename).name)


@app.get("/result/{task_id}")
def get_result(task_id: str) -> Dict:
    job = service.get_job(task_id)
    if not job:
        raise HTTPException(status_code=404, detail="task not found")
    return job.to_dict()
