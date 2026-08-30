# GEO Production System Backend

FastAPI 后端，包含 GEO Agent 体系、项目服务、JWT 鉴权、JSON 存储抽象和报告生成。

## 模块

- `api/`：FastAPI 路由与 Swagger
- `services/`：GEO 项目服务与用户鉴权
- `agents/`：Input Parser、Company、Business、Keyword、Persona、Content、Strategy、Monitor、Score、Report Agent
- `workflow/`：GEO Pipeline
- `database/`：StorageBackend 抽象，当前 JSON 实现
- `config/`：环境配置
- `prompts/`、`templates/`、`report_templates/`：Agent 与报告模板

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
