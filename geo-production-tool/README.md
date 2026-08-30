# GEO Production System V2.0

内部 GEO 服务交付工具，将客户企业资料自动转换为 GEO 优化交付方案。

## 当前能力

- 输入解析 Input Parser Agent：支持 xlsx/docx/pdf/URL
- 企业分析 Company Agent
- 业务拆解 Business Agent
- GEO关键词生成 Keyword Agent
- 用户画像 Persona Agent
- 30天内容规划 Content Agent
- GEO优化策略 Strategy Agent
- 企业级交付报告 Report Agent：docx + pdf
- 报告模板 `report_templates/geo_report_template.docx`
- FastAPI 服务层：项目任务、结果查询、文件下载
- React + Vite + Ant Design 内部控制台：Dashboard、创建项目、项目详情、报告下载

## 执行流程

```text
客户资料
  -> InputParserAgent
  -> CompanyAgent
  -> BusinessAgent
  -> KeywordAgent
  -> PersonaAgent
  -> ContentAgent
  -> StrategyAgent
  -> ReportAgent
```

## 运行方式

```bash
cd geo-production-tool
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/create_demo_inputs.py
python scripts/create_report_template.py
python main.py
```

默认读取 `input/demo_customer.xlsx`，输出文件生成到 `output/`，包括：

- `output/GEO客户分析报告.docx`
- `output/GEO客户分析报告.pdf`
- `output/keyword_matrix.xlsx`
- `output/persona_report.docx`
- `output/content_plan.xlsx`
- `output/customer_profile.json`
- `output/business_analysis.json`
- `output/strategy_plan.json`

## 本地运行

### 后端

```bash
cd geo-production-tool
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

浏览器打开 `http://127.0.0.1:5173/`，后端 Swagger 位于 `http://127.0.0.1:8000/docs`。

## API 服务

接口：

- `GET /health`：服务状态与版本
- `POST /analyze`：上传客户资料并创建分析任务，支持 `customer_name`、`website`、`industry` 表单字段
- `GET /projects`：项目列表与 Dashboard 统计
- `GET /projects/{task_id}`：项目详情与分析结果
- `GET /projects/{task_id}/download/{filename}`：下载 docx / pdf / xlsx 交付文件
- `GET /result/{task_id}`：兼容查询任务结果

API 任务输出默认保存在 `output/tasks/{task_id}/`，上传文件保存在 `storage/uploads/`。
