# GEO Production System Backend

FastAPI 后端，包含 GEO Agent 体系、项目服务、JWT 鉴权、JSON 存储抽象和报告生成。

## 模块

- `api/`：FastAPI 路由与 Swagger
- `services/`：GEO 项目服务与用户鉴权
- `services/document_service.py`：企业资料异步解析任务
- `services/geo_analysis_service.py`：独立 GEO Analysis 异步任务与 JSON 项目存储
- `agents/`：Knowledge Extract、Input Parser、Company、Business、Keyword、Persona、Content、Strategy、Monitor、Score、Report Agent
- `app/document_engine/`：MarkItDown 解析、Markdown 标准化、文本切片、知识分类
- `geo_analysis_loader.py`：加载 `apps/geo-analysis/` 独立模块
- `workflow/`：GEO Pipeline 与 DocumentParserNode
- `database/`：StorageBackend 抽象，当前 JSON 实现
- `config/`：环境配置
- `prompts/`、`templates/`、`report_templates/`：Agent 与报告模板

## 企业资料解析

`app/document_engine/markitdown_parser.py` 封装 Microsoft MarkItDown，支持：

- PDF
- DOCX
- PPTX
- XLSX
- HTML
- TXT
- Markdown

解析结果会经过 `TextChunker` 按标题与长度切片，再由 `KnowledgeExtractAgent` 输出结构化企业知识。

本机 Python 3.9 会使用 fallback 解析器，Docker/Python 3.12 环境自动使用 MarkItDown。

## 测试

```bash
cd backend
python -m pytest tests -q
```

GEO Analysis 模块测试：

```bash
cd ..
pytest -q apps/geo-analysis/tests
```

## GEO Analysis API

- `POST /api/geo/projects`：创建 GEO 内容分析项目
- `POST /api/geo/analyze`：启动文章 / URL / HTML / Markdown / TXT 分析
- `GET /api/geo/projects`：项目列表
- `GET /api/geo/projects/{id}`：状态、进度与结果
- `GET /api/geo/projects/{id}/export`：列出 `md` / `html` / `json` / `pdf` / `svg` / `png`
- `GET /api/geo/projects/{id}/export/{filename}`：下载交付文件

## 本地启动

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
STORAGE_PATH=../storage uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## Docker

根目录执行：

```bash
docker compose up -d --build
```
