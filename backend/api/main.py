"""GEO Production Tool FastAPI entry point."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Dict, Optional

from fastapi import Depends, FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from api.deps import get_current_user, get_optional_user, require_roles
from config.settings import CORS_ORIGINS, VERSION
from services.geo_service import GeoService, UPLOAD_DIR
from services.auth_service import AuthService, User, get_auth_service
from services.document_service import DocumentService
from services.geo_analysis_service import GeoAnalysisService

ALLOWED_EXTENSIONS = {".xlsx", ".docx", ".pdf"}
DOCUMENT_ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".pptx",
    ".xlsx",
    ".html",
    ".htm",
    ".txt",
    ".md",
}

service = GeoService()
auth_service = get_auth_service()
document_service = DocumentService()
geo_analysis_service = GeoAnalysisService()
app = FastAPI(
    title="GEO Production System Beta API",
    description="GEO 内部交付平台 Beta API。",
    version=VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "running", "service": "geo-production-system", "version": VERSION}


class LoginRequest(BaseModel):
    username: str
    password: str


class UpdateProjectRequest(BaseModel):
    owner: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None


class CreateGeoProjectRequest(BaseModel):
    name: str
    source: str = ""


class AnalyzeGeoRequest(BaseModel):
    project_id: str = ""
    name: str = "GEO Analysis Project"
    source: str = ""
    source_type: str = "text"
    content: str = ""
    product_description: str = ""
    company_info: str = ""


@app.post("/login")
def login(payload: LoginRequest) -> Dict:
    user = auth_service.authenticate(payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="invalid username or password")
    return {
        "token": auth_service.create_token(user),
        "token_type": "bearer",
        "user": user.to_public_dict(),
    }


@app.get("/users/me")
def get_me(user: User = Depends(get_current_user)) -> Dict:
    return user.to_public_dict()


@app.get("/users")
def list_users(user: User = Depends(require_roles("ADMIN", "MANAGER"))) -> Dict:
    return {
        "users": [item.to_public_dict() for item in auth_service.list_users()],
    }


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    customer_name: str = Form(""),
    website: str = Form(""),
    industry: str = Form(""),
    sync: bool = Query(False),
    user: User = Depends(require_roles("ADMIN", "MANAGER", "MEMBER")),
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
    upload_dir = UPLOAD_DIR / task_id
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
            owner=user.username,
        )
    else:
        job = service.start_analysis(
            source_path,
            task_id=task_id,
            customer_name=customer_name,
            website=website,
            industry=industry,
            owner=user.username,
        )
    return job.to_dict()


async def _save_document_upload(
    file: UploadFile,
    customer_name: str,
    website: str,
    industry: str,
    user: User,
) -> Dict:
    filename = file.filename or "document.xlsx"
    suffix = Path(filename).suffix.lower()
    if suffix not in DOCUMENT_ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="unsupported document type, expected pdf/docx/pptx/xlsx/html/txt/md",
        )

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="uploaded document is empty")

    task_id = uuid.uuid4().hex[:12]
    document_dir = UPLOAD_DIR / "documents" / task_id
    document_dir.mkdir(parents=True, exist_ok=True)
    source_path = document_dir / f"source{suffix}"
    source_path.write_bytes(content)

    task = document_service.start_upload(source_path, original_filename=filename)
    return {
        "task_id": task.task_id,
        "status": task.status,
        "progress": task.progress,
        "customer_name": customer_name,
        "website": website,
        "industry": industry,
        "owner": user.username,
    }


@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    customer_name: str = Form(""),
    website: str = Form(""),
    industry: str = Form(""),
    user: User = Depends(require_roles("ADMIN", "MANAGER", "MEMBER")),
) -> Dict:
    return await _save_document_upload(file, customer_name, website, industry, user)


@app.post("/api/documents/upload")
async def api_upload_document(
    file: UploadFile = File(...),
    customer_name: str = Form(""),
    website: str = Form(""),
    industry: str = Form(""),
    user: User = Depends(require_roles("ADMIN", "MANAGER", "MEMBER")),
) -> Dict:
    return await _save_document_upload(file, customer_name, website, industry, user)


@app.get("/documents/{task_id}")
def get_document_task(
    task_id: str,
    user: User = Depends(get_current_user),
) -> Dict:
    task = document_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="document task not found")
    return task.to_dict()


@app.get("/api/documents/{task_id}")
def api_get_document_task(
    task_id: str,
    user: User = Depends(get_current_user),
) -> Dict:
    task = document_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="document task not found")
    return task.to_dict()


@app.post("/projects/create")
async def create_project(
    customer_name: str = Form(""),
    website: str = Form(""),
    industry: str = Form(""),
    owner: str = Form(""),
    file: Optional[UploadFile] = File(None),
    sync: bool = Query(False),
    user: User = Depends(require_roles("ADMIN", "MANAGER", "MEMBER")),
) -> Dict:
    if not customer_name.strip():
        raise HTTPException(status_code=400, detail="customer_name is required")

    resolved_owner = owner.strip() or user.username
    source_path: Optional[Path] = None
    if file and file.filename:
        suffix = Path(file.filename).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="unsupported file type, expected .xlsx/.docx/.pdf",
            )
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="uploaded file is empty")
        task_id = uuid.uuid4().hex[:12]
        upload_dir = UPLOAD_DIR / task_id
        upload_dir.mkdir(parents=True, exist_ok=True)
        source_path = upload_dir / f"source{suffix}"
        source_path.write_bytes(content)
    else:
        task_id = None

    if source_path and sync:
        job = service.run_analysis(
            source_path,
            task_id=task_id,
            customer_name=customer_name,
            website=website,
            industry=industry,
            owner=resolved_owner,
        )
    elif source_path:
        job = service.start_analysis(
            source_path,
            task_id=task_id,
            customer_name=customer_name,
            website=website,
            industry=industry,
            owner=resolved_owner,
        )
    else:
        job = service.create_project(
            customer_name=customer_name,
            website=website,
            industry=industry,
            owner=resolved_owner,
        )
    return job.to_dict()


@app.get("/projects")
def list_projects(user: User = Depends(get_current_user)) -> Dict:
    return {
        "projects": [job.to_dict() for job in service.list_jobs()],
        "stats": service.get_stats(),
    }


@app.get("/projects/{task_id}")
def get_project(
    task_id: str,
    user: User = Depends(get_current_user),
) -> Dict:
    detail = service.get_project_detail(task_id)
    if not detail:
        raise HTTPException(status_code=404, detail="project not found")
    return detail


@app.post("/projects/{task_id}/rerun")
def rerun_project(
    task_id: str,
    user: User = Depends(require_roles("ADMIN", "MANAGER", "MEMBER")),
) -> Dict:
    job, error = service.rerun_project(task_id)
    if not job:
        status_code = {
            "not_found": 404,
            "active": 409,
            "missing_source": 400,
        }.get(error, 400)
        detail = {
            "not_found": "project not found",
            "active": "project is still processing",
            "missing_source": "source file not found",
        }.get(error, "rerun failed")
        raise HTTPException(status_code=status_code, detail=detail)
    return job.to_dict()


@app.patch("/projects/{task_id}")
def patch_project(
    task_id: str,
    payload: UpdateProjectRequest,
    user: User = Depends(require_roles("ADMIN", "MANAGER")),
) -> Dict:
    job, error = service.update_project(
        task_id,
        owner=payload.owner,
        website=payload.website,
        industry=payload.industry,
    )
    if not job:
        status_code = 404 if error == "not_found" else 409
        detail = "project not found" if error == "not_found" else "project is still processing"
        raise HTTPException(status_code=status_code, detail=detail)
    return job.to_dict()


@app.delete("/projects/{task_id}")
def delete_project(
    task_id: str,
    user: User = Depends(require_roles("ADMIN", "MANAGER", "MEMBER")),
) -> Dict:
    deleted, error = service.delete_project(task_id)
    if not deleted:
        status_code = 404 if error == "not_found" else 409
        detail = "project not found" if error == "not_found" else "project is still processing"
        raise HTTPException(status_code=status_code, detail=detail)
    return {"id": task_id, "status": "deleted"}


@app.get("/projects/{task_id}/download/{filename}")
def download_project_file(
    task_id: str,
    filename: str,
    user: Optional[User] = Depends(get_optional_user),
) -> FileResponse:
    if not user:
        raise HTTPException(status_code=401, detail="authentication required")
    file_path = service.get_output_path(task_id, filename)
    if not file_path:
        raise HTTPException(status_code=404, detail="output file not found")
    return FileResponse(str(file_path), filename=Path(filename).name)


@app.get("/result/{task_id}")
def get_result(
    task_id: str,
    user: User = Depends(get_current_user),
) -> Dict:
    job = service.get_job(task_id)
    if not job:
        raise HTTPException(status_code=404, detail="task not found")
    return job.to_dict()


@app.get("/tasks/{task_id}")
def get_task(
    task_id: str,
    user: User = Depends(get_current_user),
) -> Dict:
    detail = service.get_project_detail(task_id)
    if not detail:
        raise HTTPException(status_code=404, detail="task not found")
    return detail


@app.post("/api/geo/projects")
def create_geo_project(
    payload: CreateGeoProjectRequest,
    user: User = Depends(require_roles("ADMIN", "MANAGER", "MEMBER")),
) -> Dict:
    if not payload.name.strip():
        raise HTTPException(status_code=400, detail="project name is required")
    return geo_analysis_service.create_project(payload.name, payload.source)


@app.post("/api/geo/analyze")
def analyze_geo_project(
    payload: AnalyzeGeoRequest,
    sync: bool = Query(False),
    user: User = Depends(require_roles("ADMIN", "MANAGER", "MEMBER")),
) -> Dict:
    if payload.source_type not in {"url", "html", "markdown", "txt", "text"}:
        raise HTTPException(status_code=400, detail="unsupported source_type")
    project_id = payload.project_id.strip()
    if project_id:
        existing = geo_analysis_service.get_project(project_id)
        if not existing:
            raise HTTPException(status_code=404, detail="geo project not found")
    else:
        project = geo_analysis_service.create_project(
            payload.name or "GEO Analysis Project",
            payload.source,
        )
        project_id = project["id"]

    input_data = {
        "name": payload.name or "GEO Analysis Project",
        "source": payload.source,
        "source_type": payload.source_type,
        "content": payload.content,
        "product_description": payload.product_description,
        "company_info": payload.company_info,
    }
    return geo_analysis_service.start_analysis(project_id, input_data, sync=sync)


@app.get("/api/geo/projects")
def list_geo_projects(
    user: User = Depends(get_current_user),
) -> Dict:
    return {"projects": geo_analysis_service.list_projects()}


@app.get("/api/geo/projects/{project_id}")
def get_geo_project(
    project_id: str,
    user: User = Depends(get_current_user),
) -> Dict:
    project = geo_analysis_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="geo project not found")
    return project


@app.get("/api/geo/projects/{project_id}/export")
def list_geo_project_exports(
    project_id: str,
    user: User = Depends(get_current_user),
) -> Dict:
    files = geo_analysis_service.list_exports(project_id)
    return {"project_id": project_id, "files": files}


@app.get("/api/geo/projects/{project_id}/export/{filename}")
def download_geo_project_export(
    project_id: str,
    filename: str,
    user: Optional[User] = Depends(get_optional_user),
) -> FileResponse:
    if not user:
        raise HTTPException(status_code=401, detail="authentication required")
    file_path = geo_analysis_service.get_export_path(project_id, filename)
    if not file_path:
        raise HTTPException(status_code=404, detail="export file not found")
    return FileResponse(str(file_path), filename=Path(filename).name)
