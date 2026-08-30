# Document Engine

企业资料解析入口，基于 Microsoft MarkItDown 构建。

## 支持格式

- PDF
- DOCX
- PPTX
- XLSX
- HTML
- TXT
- Markdown

## 模块

- `markitdown_parser.py`：封装 MarkItDown，并提供本地 fallback 提取。
- `document_pipeline.py`：解析、标准化、切片、知识分类。
- `chunker.py`：按标题和长度切片，保留上下文。
- `models.py`：Pydantic 数据模型。

## 使用

```python
from app.document_engine.document_pipeline import DocumentPipeline

result = DocumentPipeline().process("sample.docx")
print(result["document"]["content"])
print(result["chunks"])
```

MarkItDown 需要 Python 3.10+，建议使用 Python 3.12 环境运行。
