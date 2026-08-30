# GEO Analysis SVG Report Module Design

## 1. Existing GEO Workflow Analysis

The current repository is `GEO-Production-System`. The existing production flow is a customer-facing GEO delivery pipeline:

```text
Input Parser
  -> Knowledge Extract Agent
  -> Company Agent
  -> Business Agent
  -> Keyword Agent
  -> Persona Agent
  -> Content Agent
  -> Strategy Agent
  -> Monitor Agent
  -> Score Agent
  -> Report Agent
```

Key implementation facts:

- FastAPI entry: `backend/api/main.py`
- Pipeline entry: `backend/workflow/pipeline.py`
- Agent contract: each agent exposes `run(input_data)` and returns `{task, status, result, next_action}`
- Project registry: `backend/services/geo_service.py` with a thread-safe JSON-backed repository
- Reports: generated under `storage/reports/{task_id}/`
- Auth: JWT via `backend/api/deps.py`
- Frontend: React + Vite + Ant Design, with API helpers in `frontend/src/api.js`

The new GEO Analysis module must not change this pipeline. It is a separate article-analysis product used from the Reports area.

## 2. New Module Architecture

The module lives under `apps/geo-analysis/` and is imported as the Python package `geo_analysis` through a loader in the FastAPI backend.

```text
apps/geo-analysis/
  agents/
    article_analyzer.py
    entity_agent.py
    keyword_agent.py
    intent_agent.py
    framework_agent.py
    svg_agent.py
  workflow/
    geo_pipeline.py
  schemas/
    article_schema.py
    geo_schema.py
    export_schema.py
  exporters/
    markdown_exporter.py
    html_exporter.py
    pdf_exporter.py
    json_exporter.py
  svg/
    renderer.py
  storage.py
  reports/
  tests/
  README.md
```

Agent contract:

```python
class ArticleAnalyzerAgent:
    def run(self, input_data: dict) -> dict:
        return {"task": "...", "status": "success", "confidence": 0, "result": {}, "next_action": "..."}
```

Pipeline contract:

```python
class GEOAnalysisPipeline:
    def run(self, project_id: str, input_data: dict, progress_callback=None) -> dict:
        ...
```

## 3. Data Model

Storage is JSON-first to match the current repository. The store is isolated at `storage/geo_analysis/projects.json`.

```json
{
  "id": "12-hex",
  "name": "邦胜工业设备 GEO 内容分析",
  "source": "https://example.com/article",
  "status": "COMPLETED",
  "progress": 100,
  "analysis_result": {},
  "svg_file": "storage/geo_analysis/exports/12-hex/architecture.svg",
  "created_at": "2026-08-31T10:00:00+08:00",
  "updated_at": "2026-08-31T10:02:00+08:00"
}
```

`analysis_result` stores:

```json
{
  "article": {},
  "entities": [],
  "keyword_clusters": [],
  "intents": [],
  "framework": {},
  "score": {
    "entity_coverage": 0,
    "keyword_coverage": 0,
    "intent_match": 0,
    "content_structure": 0,
    "authority_score": 0
  },
  "files": []
}
```

## 4. API Design

All routes are under `/api/geo` and reuse existing JWT auth.

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/geo/projects` | Create a GEO analysis project |
| POST | `/api/geo/analyze` | Start the analysis pipeline |
| GET | `/api/geo/projects` | List GEO analysis projects |
| GET | `/api/geo/projects/{id}` | Get status, progress, and result |
| GET | `/api/geo/projects/{id}/export` | List export files |
| GET | `/api/geo/projects/{id}/export/{filename}` | Download an export file |

`POST /api/geo/analyze` body:

```json
{
  "project_id": "abc123",
  "name": "GEO Analysis Project",
  "source": "https://example.com/article",
  "source_type": "url",
  "content": "",
  "product_description": "",
  "company_info": ""
}
```

`GET /api/geo/projects/{id}` response:

```json
{
  "id": "abc123",
  "name": "GEO Analysis Project",
  "source": "https://example.com/article",
  "status": "PROCESSING",
  "progress": 45,
  "analysis_result": {},
  "svg_file": "",
  "created_at": "2026-08-31T10:00:00+08:00",
  "updated_at": "2026-08-31T10:00:45+08:00"
}
```

## 5. Export Design

Each completed project writes:

```text
storage/geo_analysis/exports/{project_id}/
  analysis.json
  report.md
  report.html
  report.pdf
  architecture.svg
  architecture.png
```

Export format:

- Markdown: portable text report
- HTML: standalone report with embedded SVG
- JSON: machine-readable analysis data
- SVG: pure vector architecture diagram with groups `title`, `layers`, `nodes`, `edges`, `labels`
- PDF: reportlab-generated report
- PNG: optional `cairosvg` raster conversion, generated when the library is available

## 6. Frontend Flow

Routes:

```text
/reports/geo-analysis
/reports/geo-analysis/new
/reports/geo-analysis/:id
```

Wizard flow:

1. Article Input: URL, Markdown/HTML/TXT content, product description, company information
2. AI Analysis: create project and start `/api/geo/analyze`
3. Framework: poll project status and show framework stage
4. SVG: render generated architecture SVG
5. Export: download Markdown, HTML, JSON, PDF, SVG, PNG

The SVG viewer supports zoom, fullscreen, and download without depending on an image service.

## 7. Isolation and Testing

Rules:

- No changes to `backend/workflow/pipeline.py` or existing report agents
- No changes to existing `/analyze` and `/projects` behavior
- New backend routes import only the new module loader
- Tests use a sample article and do not require network access

Test scope:

- Article analyzer
- Entity extraction
- Keyword clustering
- Intent analysis
- Framework generation
- SVG generation
- Markdown/HTML/JSON/PDF export
- Full pipeline run
