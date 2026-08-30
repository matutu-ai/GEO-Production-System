# GEO Production Tool V1.5

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
- FastAPI 服务层：上传客户资料并运行完整 GEO Pipeline

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

## API 服务

启动：

```bash
uvicorn api.main:app --reload
```

打开 `http://127.0.0.1:8000/docs` 可查看 Swagger 接口。

接口：

- `GET /health`：服务状态与版本
- `POST /analyze`：上传 `.xlsx` / `.docx` / `.pdf` 客户资料，返回 `task_id` 和输出文件
- `GET /result/{task_id}`：查询任务结果

API 任务输出默认保存在 `output/tasks/{task_id}/`，上传文件保存在 `storage/uploads/`。
