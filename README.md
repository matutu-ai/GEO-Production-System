# GEO Production System

GEO（Generative Engine Optimization）内部交付平台，用于将客户企业资料自动转换为 ChatGPT、Claude、Gemini、DeepSeek 等 AI 搜索中的品牌曝光优化方案。

## 功能

- 企业资料解析：支持 `.pdf`、`.docx`、`.pptx`、`.xlsx`、`.html`、`.txt`、`.md`
- Agent 流水线：文档解析、知识抽取、企业分析、业务拆解、关键词、用户画像、内容规划、GEO 策略、监控、评分、报告
- 交付报告：`docx`、`pdf`、`xlsx`、`json`
- GEO 内容分析：URL / HTML / Markdown / TXT → 实体、关键词簇、搜索意图、内容框架、GEO 评分 → SVG 架构图 → `md` / `html` / `json` / `pdf` / `svg` / `png`
- 项目管理：创建、查看、重跑、删除、状态流转
- 用户权限：ADMIN / MANAGER / MEMBER / CLIENT，JWT 登录
- 内部控制台：Dashboard、创建项目、项目详情、报告中心
- Docker 一键部署：前端 Nginx + 后端 FastAPI

## 技术架构

- Backend：Python 3.12、FastAPI、uvicorn
- Frontend：React、Vite、Ant Design、Nginx
- Agent Runtime：Python Agent + Pipeline
- Storage：JSON 存储抽象，预留数据库替换
- Auth：JWT
- Deployment：Docker Compose

## 系统架构

```mermaid
flowchart LR
    Web[Web Console<br/>React + Vite + Ant Design] --> API[FastAPI API]
    API --> Auth[JWT Auth]
    API --> GS[GeoService]
    GS --> ST[JSON Storage<br/>预留数据库替换]
    GS --> PL[GEO Pipeline]
    PL --> Parser[Input Parser Agent]
    Parser --> Doc[Document Parser Node<br/>MarkItDown + Chunker]
    Doc --> Knowledge[Knowledge Extract Agent]
    Knowledge --> Company[Company Agent]
    Company --> Business[Business Agent]
    Business --> Keyword[Keyword Agent]
    Keyword --> Persona[Persona Agent]
    Persona --> Content[Content Agent]
    Content --> Strategy[Strategy Agent]
    Strategy --> Monitor[Monitor Agent]
    Monitor --> Score[GEO Score Agent]
    Score --> Report[Report Agent]
    Report --> Files[deliverables<br/>docx / pdf / xlsx / json]
```

## 目录结构

```text
GEO-Production-System/
├── backend/
│   ├── api/                 # FastAPI 路由
│   ├── agents/              # GEO Agent 体系
│   │   └── knowledge_agent/ # 企业资料知识抽取
│   ├── workflow/            # GEO Pipeline
│   ├── services/            # 项目服务与鉴权
│   ├── app/
│   │   └── document_engine/ # MarkItDown 解析与文本切片
│   ├── database/            # StorageBackend 抽象
│   ├── config/              # 环境配置
│   ├── prompts/             # Agent Prompt
│   ├── templates/           # 报告模板
│   ├── report_templates/    # docx 模板
│   ├── scripts/             # 本地初始化脚本
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/                 # React 页面与组件
│   ├── Dockerfile
│   └── nginx.conf
├── storage/
│   ├── projects/            # 项目注册表
│   ├── uploads/             # 上传资料
│   ├── reports/             # 项目交付报告
│   └── users/               # 默认用户
├── docs/
│   └── screenshots/
├── apps/
│   └── geo-analysis/       # 独立 GEO Analysis 模块与 SVG 报告引擎
├── deploy/
│   ├── nginx/geo.http.conf.example # Certbot 前的 HTTP 入口
│   ├── nginx/geo.conf.example   # 最终 HTTPS 配置示例
│   ├── server_setup.sh          # Ubuntu 生产部署脚本
│   └── README.md                # 生产部署说明
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
└── .gitignore
```

## 环境变量说明

| 变量 | 说明 | 默认值 |
| --- | --- | --- |
| `APP_ENV` | 运行环境 | `production` |
| `APP_VERSION` | API 版本 | `2.2.0` |
| `API_BASE_URL` | Docker 构建时写入前端的 API 地址 | `https://api.housun.shop` |
| `CORS_ORIGINS` | 后端允许的跨域前端地址 | `https://housun.shop` |
| `OPENAI_API_KEY` | OpenAI/兼容模型密钥，空值使用 Mock | 空 |
| `MODEL_NAME` | 模型名称 | `gpt-4o-mini` |
| `MODEL_PROVIDER` | 模型提供方，预留切换 | `mock` |
| `STORAGE_BACKEND` | 存储后端，当前 JSON | `json` |
| `STORAGE_PATH` | 项目、上传和报告存储目录 | `/app/storage` |
| `JWT_SECRET` | JWT 签名密钥，生产必须替换 | 本地默认值 |
| `JWT_EXPIRE_MINUTES` | Token 有效期 | `1440` |
| `VITE_API_URL` | Cloudflare Pages / 前端构建时 API 基础地址 | `https://api.housun.shop` |

生产环境不要提交 `.env`，并确保 `JWT_SECRET`、`OPENAI_API_KEY` 已替换为真实值。

## API 说明

Swagger 页面：`http://127.0.0.1:8000/docs`

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/health` | 健康检查 |
| `POST` | `/login` | 登录并返回 JWT |
| `GET` | `/users/me` | 当前用户 |
| `GET` | `/users` | 用户列表，ADMIN/MANAGER |
| `POST` | `/analyze` | 上传资料并执行 GEO 分析 |
| `POST` | `/projects/create` | 创建 GEO 项目 |
| `GET` | `/projects` | 项目列表与统计 |
| `GET` | `/projects/{id}` | 项目详情 |
| `POST` | `/projects/{id}/rerun` | 重新运行分析 |
| `PATCH` | `/projects/{id}` | 更新项目 |
| `DELETE` | `/projects/{id}` | 删除项目 |
| `GET` | `/projects/{id}/download/{filename}` | 下载交付文件 |
| `GET` | `/result/{id}` | 查询任务结果 |
| `POST` | `/documents/upload` | 上传企业资料，异步解析为知识块 |
| `GET` | `/documents/{task_id}` | 查询文档解析任务状态与结果 |
| `POST` | `/api/geo/projects` | 创建 GEO 内容分析项目 |
| `POST` | `/api/geo/analyze` | 启动 GEO Analysis Pipeline |
| `GET` | `/api/geo/projects` | GEO 分析项目列表 |
| `GET` | `/api/geo/projects/{id}` | 查询 GEO 分析状态、进度与结果 |
| `GET` | `/api/geo/projects/{id}/export` | 列出 GEO 分析交付文件 |
| `GET` | `/api/geo/projects/{id}/export/{filename}` | 下载 GEO 分析交付文件 |

## 本地启动

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
STORAGE_PATH=../storage uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Swagger：`http://127.0.0.1:8000/docs`

MarkItDown 需要 Python 3.10+，生产容器使用 Python 3.12。Python 3.9 本地环境会自动使用内置 fallback 解析器，覆盖 demo 所需的 `docx`、`pdf`、`xlsx`。

### 企业资料解析

```bash
cd backend
python - <<'PY'
from app.document_engine.document_pipeline import DocumentPipeline
result = DocumentPipeline().process("input/demo_customer.docx")
print(result["document"]["content"])
print([chunk["chunk_id"] for chunk in result["chunks"]])
PY
```

解析接口：

- `POST /documents/upload`：上传资料后返回 `task_id`、`status`、`progress`
- `GET /documents/{task_id}`：返回 `uploading / parsing / extracting / generating / completed / failed` 状态与 `knowledge` 结果

进度映射：`uploading=0`、`parsing=20`、`extracting=50`、`generating=80`、`completed=100`。

### Frontend

```bash
cd frontend
npm install
npm run dev
```

控制台：`http://127.0.0.1:5173/`

GEO 分析中心：

- `/reports/geo-analysis`：GEO Analysis 项目列表
- `/reports/geo-analysis/new`：创建文章 / URL / Markdown / HTML / TXT 分析
- `/reports/geo-analysis/:id`：GEO 评分、内容框架、SVG 架构图与交付文件下载

默认账号：

- 管理员：`admin / admin123`
- 负责人：`manager / manager123`
- 执行人员：`member / member123`
- 客户：`client / client123`

### 本地流水线

```bash
cd backend
source .venv/bin/activate
python main.py
```

默认读取 `backend/input/demo_customer.xlsx`，输出到 `backend/output/`。

### 公网任务状态验证

本机 Python TLS 不稳定时，可使用 curl 包装脚本检查线上异步任务状态：

```bash
python scripts/check_task_status.py
```

脚本会自动登录、从项目列表选择一个已完成任务，并写入 `task_status.log`。

常用参数：

```bash
python scripts/check_task_status.py \
  --task-id 558e31d89a64 \
  --url https://api.housun.shop \
  --max-attempts 30 \
  --poll-interval 2
```

可通过环境变量覆盖默认配置：

- `GEO_API_URL`
- `GEO_API_TOKEN`
- `GEO_API_USERNAME`
- `GEO_API_PASSWORD`
- `GEO_TASK_ID`
- `GEO_STATUS_LOG`

## Docker 启动

```bash
cp .env.example .env
docker compose build
docker compose up -d
```

访问：

- 前端：`http://localhost:8080`
- 后端 API：`http://localhost:8000/docs`
- 健康检查：`http://localhost:8000/health`

常用命令：

```bash
docker compose ps
docker compose logs -f backend
docker compose logs -f frontend
docker compose down
```

`storage/` 挂载到后端容器 `/app/storage`，项目、上传文件和报告都会持久化在宿主机。

生产环境由宿主机 Nginx 接管 `80/443`，Docker 服务只监听本机回环地址，避免端口冲突。

```text
用户
  -> https://geo.example.com
     -> Nginx
        -> frontend 容器 127.0.0.1:8080
  -> https://api.geo.example.com
     -> Nginx
        -> backend 容器 127.0.0.1:8000
```

## 生产部署

### 1. 服务器准备

Ubuntu 22.04/24.04，并把以下 DNS 指向服务器公网 IP：

```bash
geo.example.com -> 服务器 IP
api.geo.example.com -> 服务器 IP
```

安装 Docker、Nginx、Certbot：

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo apt-get update
sudo apt-get install -y docker-compose-plugin nginx certbot python3-certbot-nginx
```

### 2. 拉取代码并配置

```bash
sudo git clone <repository-url> /opt/geo-production-system
cd /opt/geo-production-system
sudo cp .env.example .env
sudo cp frontend/.env.production.example frontend/.env.production
```

修改 `.env`：

```bash
API_BASE_URL=https://api.geo.example.com
OPENAI_API_KEY=your-key
MODEL_NAME=gpt-4o-mini
JWT_SECRET=replace-with-a-long-random-secret
```

### 3. 启动生产容器

```bash
sudo docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
sudo docker compose -f docker-compose.yml -f docker-compose.prod.yml ps
curl http://127.0.0.1:8000/health
```

### 4. 安装宿主机 Nginx HTTP 入口

```bash
sudo cp deploy/nginx/geo.http.conf.example /etc/nginx/sites-available/geo.conf
sudo ln -sfn /etc/nginx/sites-available/geo.conf /etc/nginx/sites-enabled/geo.conf
sudo nginx -t
sudo systemctl reload nginx
```

### 5. 申请 HTTPS

```bash
sudo certbot --nginx -d geo.example.com
sudo certbot --nginx -d api.geo.example.com
sudo systemctl reload nginx
```

### 6. 验证

```bash
curl -I https://geo.example.com
curl https://api.geo.example.com/health
```

浏览器访问 `https://geo.example.com`，上传 `backend/input/demo_customer.xlsx`，执行 GEO 分析并下载报告。

完整服务器部署脚本和 Nginx 示例见 [deploy/README.md](deploy/README.md) 与 [deploy/nginx/](deploy/nginx/)。
