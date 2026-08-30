# GEO Production System

GEO（Generative Engine Optimization）内部交付平台，用于将客户企业资料自动转换为 ChatGPT、Claude、Gemini、DeepSeek 等 AI 搜索中的品牌曝光优化方案。

## 功能

- 客户资料解析：支持 `.xlsx`、`.docx`、`.pdf`
- Agent 流水线：企业分析、业务拆解、关键词、用户画像、内容规划、GEO 策略、监控、评分、报告
- 交付报告：`docx`、`pdf`、`xlsx`、`json`
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

## 目录结构

```text
GEO-Production-System/
├── backend/
│   ├── api/                 # FastAPI 路由
│   ├── agents/              # GEO Agent 体系
│   ├── workflow/            # GEO Pipeline
│   ├── services/            # 项目服务与鉴权
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
├── docker-compose.yml
├── .env.example
└── .gitignore
```

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

### Frontend

```bash
cd frontend
npm install
npm run dev
```

控制台：`http://127.0.0.1:5173/`

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

## Docker 启动

```bash
cp .env.example .env
docker compose build
docker compose up -d
```

访问：

- 前端：`http://localhost`
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

## Ubuntu 服务器部署

1. 安装 Docker 与 Compose 插件：

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

2. 拉取项目并配置：

```bash
git clone <repository-url>
cd <repository>
cp .env.example .env
docker compose up -d --build
```

3. 验证：

```bash
docker compose ps
curl http://127.0.0.1:8000/health
```

前端默认监听 `80`，后端监听 `8000`。生产环境建议在服务器前接入 HTTPS 反向代理，并把 `.env` 中的 `JWT_SECRET`、`OPENAI_API_KEY` 替换为真实配置。
