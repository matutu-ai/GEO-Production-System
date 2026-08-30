# GEO Analysis Module

Independent article and content-analysis module for the GEO Production System.

## Pipeline

```text
Article URL / HTML / Markdown / TXT
  -> Article Analyzer Agent
  -> GEO Entity Analysis
  -> Keyword Cluster Analysis
  -> Search Intent Analysis
  -> Content Framework Generation
  -> SVG Architecture Generation
  -> Report Export
```

## Output

Each project exports:

- `analysis.json`
- `report.md`
- `report.html`
- `report.pdf`
- `architecture.svg`
- `architecture.png` when `cairosvg` is installed

## Run

From the repository root:

```bash
python -m pytest apps/geo-analysis/tests
```

For API integration, see `backend/api/main.py` routes under `/api/geo`.
