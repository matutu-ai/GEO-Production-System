from geo_analysis.agents.article_analyzer import ArticleAnalyzerAgent


def test_article_analyzer_returns_structured_result(sample_input):
    result = ArticleAnalyzerAgent().run(sample_input)

    assert result["status"] == "success"
    assert result["result"]["title"]
    assert result["result"]["summary"]
    assert len(result["result"]["topics"]) >= 3
    assert len(result["result"]["keywords"]) >= 5


def test_article_analyzer_handles_markdown():
    content = """# GEO Visibility Guide

This article explains how brands can appear in ChatGPT, Claude and Gemini answers.
"""
    result = ArticleAnalyzerAgent().run(
        {
            "name": "GEO Visibility Guide",
            "source": "",
            "source_type": "markdown",
            "content": content,
            "product_description": "",
            "company_info": "",
        }
    )

    assert result["status"] == "success"
    assert result["result"]["title"] == "GEO Visibility Guide"
