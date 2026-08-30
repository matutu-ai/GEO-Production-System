# GEO Analysis Workflow

The pipeline is a simple state-machine sequence:

```text
Article Analyzer
-> Entity Analysis
-> Keyword Cluster Analysis
-> Search Intent Analysis
-> Content Framework Generation
-> SVG Architecture Generation
-> Report Export
```

It accepts a progress callback `(stage, progress)` so the API can persist status updates.
