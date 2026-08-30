# GEO Analysis Agents

Each agent exposes a `run(input_data)` method and returns a uniform result dict.

- `article_analyzer.py`: normalize URL/HTML/Markdown/TXT input
- `entity_agent.py`: extract brand, product, organization, location, person entities
- `keyword_agent.py`: generate primary, secondary, semantic and cluster keywords
- `intent_agent.py`: classify search intent and build an intent map
- `framework_agent.py`: generate content structure, FAQ, schema and recommendations
- `svg_agent.py`: generate the pure-SVG architecture diagram
