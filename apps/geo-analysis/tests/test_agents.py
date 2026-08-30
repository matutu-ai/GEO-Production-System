from geo_analysis.agents.entity_agent import EntityAgent
from geo_analysis.agents.framework_agent import FrameworkAgent
from geo_analysis.agents.intent_agent import IntentAgent
from geo_analysis.agents.keyword_agent import KeywordAgent
from geo_analysis.agents.svg_agent import SVGAgent
from geo_analysis.workflow.geo_pipeline import GEOAnalysisPipeline


def test_entity_agent_extracts_brand_and_products(sample_input):
    article = {
        "title": "Automatic Packaging Machines GEO Guide",
        "summary": "Industrial automation packaging guide.",
        "content": sample_input["content"],
        "keywords": ["packaging", "case erector"],
        "topics": ["Packaging", "Automation"],
    }
    result = EntityAgent().run({"article": article, "input_data": sample_input})

    assert result["status"] == "success"
    names = [entity["name"] for entity in result["result"]["entities"]]
    assert any("Bang Sheng" in name for name in names)
    assert any("case erector" in name.lower() for name in names)


def test_keyword_intent_framework_and_svg(sample_input):
    pipeline = GEOAnalysisPipeline()
    article_result = pipeline.run(
        "agent-test",
        sample_input,
        lambda stage, progress: None,
    )
    assert article_result["status"] == "success"
    result = article_result["result"]

    keyword_result = KeywordAgent().run(
        {
            "article": result["article"],
            "entities": result["entities"],
            "input_data": sample_input,
        }
    )
    assert keyword_result["status"] == "success"
    assert len(keyword_result["result"]) >= 4

    intent_result = IntentAgent().run({"keyword_clusters": keyword_result["result"]})
    assert intent_result["status"] == "success"
    assert {item["intent"] for item in intent_result["result"]} == {
        "informational",
        "commercial",
        "transactional",
        "navigational",
    }

    framework_result = FrameworkAgent().run(
        {
            "article": result["article"],
            "keyword_clusters": keyword_result["result"],
            "intents": intent_result["result"],
        }
    )
    assert framework_result["status"] == "success"
    assert len(framework_result["result"]["structure"]) >= 6
    assert framework_result["result"]["faq"]
    assert framework_result["result"]["schema"]

    svg_result = SVGAgent().run(
        {
            "article": result["article"],
            "framework": framework_result["result"],
            "keyword_clusters": keyword_result["result"],
            "intents": intent_result["result"],
        }
    )
    assert svg_result["status"] == "success"
    assert svg_result["result"]["svg"].startswith("<?xml")
    for group in ("title", "layers", "nodes", "edges", "labels"):
        assert f'id="{group}"' in svg_result["result"]["svg"]
